from storages.backends.s3boto import S3BotoStorage
from settings import AWS_SECRET_ACCESS_KEY

StaticS3BotoStorage = lambda: S3BotoStorage(location='static')
MediaS3BotoStorage = lambda: S3BotoStorage(location='media')

import os
import base64
import hmac, hashlib

policy_document = '''
{"expiration": "2020-01-01T00:00:00Z",
  "conditions": [
    {"bucket": "geekbar_bucket"},
    ["starts-with", "$key", "media/"],
    {"acl": "public-read"},
    ["starts-with", "$Content-Type", "image/"],
    ["starts-with", "$csrfmiddlewaretoken", ""],
    ["content-length-range", 0, 1048576]
  ]
}
'''

policy = base64.b64encode(policy_document)
signature = base64.b64encode(hmac.new(AWS_SECRET_ACCESS_KEY, policy, hashlib.sha1).digest())

