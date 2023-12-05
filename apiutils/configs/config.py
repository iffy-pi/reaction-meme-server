import os
# Relies on config file location so if config file is moved, make sure to update path finding
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.split(__file__)[0], '..', '..'))

CLOUDINARY_CLOUD_NAME = os.environ.get('RMSVR_CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('RMSVR_CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('RMSVR_CLOUDINARY_API_SECRET')
PBFS_ACCESS_TOKEN = os.environ.get('RMSVR_PBFS_ACCESS_TOKEN')
PBFS_SERVER_IDENTIFIER = os.environ.get('RMSVR_PBFS_SERVER_IDEN')