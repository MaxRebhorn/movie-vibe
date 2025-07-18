from django.test import TestCase
from movies.models import Movie
from django.core.exceptions import ValidationError
from datetime import date, timedelta
import json


