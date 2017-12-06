'''
views.py: part of expfactory package

Copyright (c) 2017, Vanessa Sochat
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

from flask import (
    flash,
    jsonify,
    render_template, 
    request, 
    redirect,
    session
)

from flask_wtf.csrf import generate_csrf
from flask_cors import cross_origin
from expfactory.defaults import EXPFACTORY_LOGS
from werkzeug import secure_filename
from expfactory.utils import get_post_fields

from expfactory.views.utils import (
    perform_checks, 
    clear_session
)
from expfactory.server import app
from .general import *

from random import choice
import logging
import os
import json

from expfactory.forms import (
    ParticipantForm,
    EntryForm
)


# LOGGING ######################################################################

file_handler = logging.FileHandler("%s/expfactory.log" % EXPFACTORY_LOGS)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)


# SECURITY #####################################################################

@app.after_request
def inject_csrf_token(response):
    response.headers.set('X-CSRF-Token', generate_csrf())
    return response
  

# EXPERIMENT PORTAL ############################################################

@app.route('/experiments')
def experiment_base():
    return render_template('experiments/index.html')


# Home portal to start experiments
@app.route('/', methods=['GET', 'POST'])
def home():

    # A headless app can only be entered with a user token
    if app.headless:
        if "token" not in session:
            form = EntryForm()
            return render_template('routes/entry.html', form=form)
        return redirect('/login')

    return portal()


# EXPERIMENT ROUTER ############################################################


@app.route('/save', methods=['POST'])
def save():
    '''save is a view to save data. We might want to adjust this to allow for
       updating saved data, but given single file is just one post for now
    '''
    if request.method == 'POST':
        exp_id = session.get('exp_id')

        fields = get_post_fields(request)
        result_file = app.save_data(session=session, content=fields, exp_id=exp_id)

        experiments = app.finish_experiment(session, exp_id)
        app.logger.info('Finished %s, %s remaining.' % (exp_id, len(experiments)))

        # Note, this doesn't seem to be enough to trigger ajax success
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    return json.dumps({'success':False}), 403, {'ContentType':'application/json'} 



@app.route('/next', methods=['POST', 'GET'])
def next():

    # Headless mode requires logged in user with token
    if app.headless and "token" not in session:
        return headless_denied()
    return router()
   

# Reset/Logout
@app.route('/logout', methods=['POST', 'GET'])
def logout():

    # If the user has finished, clear session
    clear_session()
    return redirect('/')


# Finish
@app.route('/finish', methods=['POST', 'GET'])
def finish():

    subid = session.get('subid')

    # If the user has finished, clear session
    if subid is not None:
        clear_session()
        return render_template('routes/finish.html')
    return redirect('/')


@app.route('/start')
def start():
    '''start a battery.
    '''
    return perform_checks('routes/start.html')
