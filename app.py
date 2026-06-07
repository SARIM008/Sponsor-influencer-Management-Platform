from init import app, db
from models import User,Sponsor,Influencer
from flask import Flask,render_template, request, redirect, url_for, flash
import routes
if __name__ == '__main__':
    app.run(debug=True)
