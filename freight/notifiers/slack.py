from __future__ import absolute_import

__all__ = ['SlackNotifier']

import json
import random

from freight import http
from freight.models import App, TaskStatus

from .base import Notifier, NotifierEvent


SQUIRRELS = [
    "http://images.cheezburger.com/completestore/2011/11/2/aa83c0c4-2123-4bd3-8097-966c9461b30c.jpg",
    "http://images.cheezburger.com/completestore/2011/11/2/46e81db3-bead-4e2e-a157-8edd0339192f.jpg",
    "http://28.media.tumblr.com/tumblr_lybw63nzPp1r5bvcto1_500.jpg",
    "http://i.imgur.com/DPVM1.png",
    "http://d2f8dzk2mhcqts.cloudfront.net/0772_PEW_Roundup/09_Squirrel.jpg",
    "http://www.cybersalt.org/images/funnypictures/s/supersquirrel.jpg",
    "http://www.zmescience.com/wp-content/uploads/2010/09/squirrel.jpg",
    "http://img70.imageshack.us/img70/4853/cutesquirrels27rn9.jpg",
    "http://img70.imageshack.us/img70/9615/cutesquirrels15ac7.jpg",
    "https://dl.dropboxusercontent.com/u/602885/github/sniper-squirrel.jpg",
    "http://1.bp.blogspot.com/_v0neUj-VDa4/TFBEbqFQcII/AAAAAAAAFBU/E8kPNmF1h1E/s640/squirrelbacca-thumb.jpg",
    "https://dl.dropboxusercontent.com/u/602885/github/soldier-squirrel.jpg",
    "https://dl.dropboxusercontent.com/u/602885/github/squirrelmobster.jpeg",
]


class SlackNotifier(Notifier):
    def get_options(self):
        return {
            'webhook_url': {'required': True},
        }

    def send(self, task, config, event):
        webhook_url = config['webhook_url']

        app = App.query.get(task.app_id)

        params = {
            'number': task.number,
            'app_name': app.name,
            'params': dict(task.params or {}),
            'env': task.environment,
            'ref': task.ref,
            'sha': task.sha[:7] if task.sha else task.ref,
            'status_label': task.status_label,
            'duration': task.duration,
            'link': http.absolute_uri('/{}/{}/{}'.format(app.name, task.environment, task.number)),
        }

        # TODO(dcramer): show the ref when it differs from the sha
        if event == NotifierEvent.TASK_QUEUED:
            title = "[{app_name}/{env}] Queued deploy <{link}|#{number}> ({sha})".format(**params)
        elif event == NotifierEvent.TASK_STARTED:
            title = "[{app_name}/{env}] Starting deploy <{link}|#{number}> ({sha})".format(**params)
        elif task.status == TaskStatus.failed:
            title = "[{app_name}/{env}] Failed to deploy <{link}|#{number}> ({sha}) after {duration}s".format(**params)
        elif task.status == TaskStatus.cancelled:
            title = "[{app_name}/{env}] Deploy <{link}|#{number}> ({sha}) was cancelled after {duration}s".format(**params)
        elif task.status == TaskStatus.finished:
            title = "[{app_name}/{env}] Successfully deployed <{link}|#{number}> ({sha}) after {duration}s ".format(**params)
            title += random.choice(SQUIRRELS)
        else:
            raise NotImplementedError(task.status)

        payload = {
            'parse': 'none',
            'text': title,
        }

        values = {'payload': json.dumps(payload)}

        http.post(webhook_url, values)
