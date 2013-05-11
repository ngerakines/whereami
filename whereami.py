
import datetime
import boto
import os
import simplejson as json
import tornado.ioloop
import tornado.web
import tornado.options
import tornado.httpclient
from tornado.options import define, options
import tornado.httpserver
import urllib

define("port", default = 5000, help = "run on the given port", type = int)
define("bucket", default = "whereami-ngerakines", help = "which amazon s3 bucket to use", type = str)

config_path = os.path.join(os.path.dirname(__file__), 'config.json')

conn = boto.connect_s3()

defaults = dict()
defaults['current_state'] = 'Unknown'

presets = dict()
presets["At Work"] = {"style": "success", "values": {"current_state": "Working", "current_location": "Blizzard Entertainment, California (PDT)", "current_geo": "33.657701, -117.766142", "gtalk": "ok", "hipchat": "ok", "skype": "ok"}}
presets["At Home"] = {"style": "danger", "values": {"current_state": "Relaxing", "current_location": "Irvine, CA", "clear_current_geo": "ok", "gtalk": "ok", "hipchat": "remove", "skype": "remove"}}
presets["Unavailable"] = {"style": "inverse", "values": {"current_state": "Unavailable", "clear_current_location": "ok", "clear_current_geo": "ok", "clear_gtalk": "ok", "clear_hipchat": "ok", "clear_skype": "ok"}}

communication_types = ['gtalk', 'skype']
keys = ['current_state', 'current_location', 'current_geo', 'best_phone', 'best_email'] + communication_types

bucket = None
cached_status = None

def load_defaults():
	try:
		with open(config_path) as f:
			config = json.loads(f)
			if "presets" in config:
				global presets
				presets = config["presets"]
			if "defaults" in config:
				global defaults
				defaults = config["defaults"]
			if "communication_types" in config:
				global communication_types
				communication_types = config["communication_types"]
			for communication_type in communication_types:
				defaults[communication_type] = "question-sign"
	except:
		pass

def setup_bucket():
	global bucket
	bucket = conn.lookup(options.bucket)
	if bucket is None:
		bucket = conn.create_bucket(options.bucket)

def key_default(key, status):
	if key in status:
		return status[key]
	if key in defaults:
		return defaults[key]
	return ''

def load_status():
	global cached_status
	setup_bucket()
	if cached_status is not None:
		return cached_status
	key = bucket.get_key('status.json')
	if key is not None and key.exists():
		cached_status = json.loads(key.get_contents_as_string())
		return cached_status
	return save_status(get_default_status())

def get_default_status():
	status = dict()
	status['last_updated'] = str(datetime.datetime.utcnow())
	status['current_state'] = 'Working'
	status['hipchat'] = 'ok'
	status['gtalk'] = 'remove'
	status['skype'] = 'question-sign'
	status['best_phone'] = '(415) 963-1165'
	status['current_location'] = 'Blizzard Entertainment, California (PDT)'
	status['current_geo'] = [33.657701, -117.766142]
	return status

def save_status(status):
	global cached_status
	cached_status = status
	json_string = json.dumps(status)
	key = bucket.get_key('status.json')
	if key is not None and key.exists():
		key.set_contents_from_string(json_string, replace = True)
	else:
		key = bucket.new_key('status.json')
		key.set_contents_from_string(json_string, replace = True)
	return status

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html', status = load_status(), communication_types = communication_types)

class AdminHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('admin.html', status = load_status(), presets = presets, communication_types = communication_types)

	def post(self):
		status = load_status()
		for key in keys:
			status[key] = self.get_argument(key, key_default(key, status))
			clear_key = "clear_%s" % key
			if self.get_argument(clear_key, False):
				status.pop(key, None)
			if key not in status:
				if  key in defaults:
					status[key] = defaults[key]
			if key == 'current_geo':
				if key in status:
					try:
						status[key] = map(float, status[key].split(","))
					except:
						pass
		status['last_updated'] = str(datetime.datetime.utcnow())
		save_status(status)
		self.redirect('/admin')

class GeoHandler(tornado.web.RequestHandler):
	def get(self):
		address = self.get_argument("address", "Irvine, CA")
		http_client = tornado.httpclient.HTTPClient()
		url = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % urllib.quote(address)
		try:
			response = http_client.fetch(url)
			response_obj = json.loads(response.body)
			if "results" in response_obj:
				if len(response_obj["results"]) > 0:
					location = response_obj["results"][0]["geometry"]["location"]
					return self.write("[%s, %s]" % (location["lat"], location["lng"]))
			return self.write(response.body)
		except tornado.httpclient.HTTPError as e:
			print "Error:", e
		http_client.close()
		self.write("OK")

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/admin", AdminHandler),
			(r"/admin/geo", GeoHandler)
		]
		settings = dict(
			template_path = os.path.join(os.path.dirname(__file__), "templates"),
			static_path = os.path.join(os.path.dirname(__file__), 'static'),
			debug = True,
		)
		tornado.web.Application.__init__(self, handlers, **settings)

def main():
	load_defaults()
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(os.environ.get("PORT", 5000))
	tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
	main()
