from fastapi import APIRouter
from controllers import *


router = APIRouter(prefix="/auth", tags=["auth appplication"])