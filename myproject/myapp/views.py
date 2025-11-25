from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection, transaction

# TODO： 给这些分个类，放进views文件夹
