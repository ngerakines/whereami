# About

whereami is a small python webapp that provides detailed presence information for an individual.

The primary use case is to keep my team and family a quick place to see what I'm doing, where I am and what my availability is.

# Before you start

This is a Python 2.7 web application that uses Tornado (3.0.1), simplejson (3.2.0) and boto (2.9.2). Data is stored and retreived from Amazon S3 in the form of JSON files.

To use this app, you must set the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY env variables. By default the S3 bucket "whereami" is used and will be created if it doesn't exist.

# Using on Horoku

This app is made to be deployed to horoku. Assuming you have heroku setup locally, you can deploy this app with the following steps:

	$ git push heroku master
	$ heroku create --stack cedar
    $ heroku config:set AWS_ACCESS_KEY_ID="YOURACCESSKEY"
    $ heroku config:set AWS_SECRET_ACCESS_KEY="YOURSECRETKEY"

# Configuration

You should update the default communication types and presets as they are currently pointing to my work and home and my own contact information. This can be done by creating a new file called "config.json" and setting the appropiate "defaults", "presets" and "communication" data structures. An example file would be:

	{
		"defaults": {
			"current_state": "Unknown",
			"best_email": "you@awesome.com",
			"best_phone": "(555) 123-4567"
		},
		"communication_types": ["gtalk", "campfire"],
		"presets": {
			"At Work": {
				"style": "success",
				"values": {
					"current_state": "Working",
					"current_location": "The Office",
					"current_geo": "0, 0",
					"gtalk": "remove",
					"campfire": "ok"
				}
			},
			"Commuting": {
				"style": "inverse",
				"values": {
					"current_state": "Traveling",
					"current_location": "Enroute to SFO from DAY via Delta",
					"clear_current_geo": "ok",
					"clear_gtalk": "ok",
					"clear_campfire": "ok"
				}
			}
		}
	}

# Errata

Some values are hardcoded to styles. For example for the current_state property the values "Working", "Relaxing", "Traveling", "Unavailable" and "Unknown" all have hardcoded text styles ala bootstrap. The same is true for communication type icons.

# License

Copyright (c) 2010 Nick Gerakines nick@gerakines.net

This project and its contents are open source under the MIT license.
