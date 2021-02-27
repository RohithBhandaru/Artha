#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 15:23:02 2020

@author: rohithbhandaru
"""


from flask_assets import Bundle


def compile_assets(assets):
    # Defining JS and CSS bundles
    moment_js_bundle = Bundle("moment.min.js", "moment-timezone-with-data-1970-2030.min.js",
                              filters="jsmin", output="public/js/moment-files.min.js")

    # Registering JS and CSS bundles
    assets.register("moment-files-js", moment_js_bundle)

    # Building JS and CSS bundles
    moment_js_bundle.build()
