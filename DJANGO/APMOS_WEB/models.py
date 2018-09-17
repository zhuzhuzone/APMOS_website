# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Trade(models.Model):
    id = models.BigAutoField(primary_key=True)
    exch_trade_id = models.CharField(unique=True, max_length=255)
    ap_code = models.CharField(max_length=64)
    exchange_code = models.CharField(max_length=8)
    side = models.CharField(max_length=8)
    price = models.FloatField()
    volume = models.BigIntegerField()
    trader_id = models.CharField(max_length=255)
    account = models.CharField(max_length=32, blank=True, null=True)
    book = models.CharField(max_length=32, blank=True, null=True)
    counterparty = models.CharField(max_length=64, blank=True, null=True)
    source = models.CharField(max_length=32, blank=True, null=True)
    is_cfd = models.PositiveIntegerField()
    trade_datetime = models.DateTimeField()
    create_datetime = models.DateTimeField()
    last_update_datetime = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Trade'


class User(models.Model):
    username = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'User'
