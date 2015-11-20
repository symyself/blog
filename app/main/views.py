# coding: utf-8
from flask import render_template,flash
from . import main

@main.route('/')
def base():
    flash('weclome')
    return render_template( 'base.html' )
