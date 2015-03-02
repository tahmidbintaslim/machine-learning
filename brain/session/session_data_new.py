#!/usr/bin/python

## @session_data_new.py
#  This file receives data (i.e. settings), including one or more dataset(s)
#      provided during the current session, and stores them into corresponding
#      database tables. The stored dataset(s) can later be retrieved from
#      'session_data_append.py', or 'session_generate_model.py'.
#
#  Note: the term 'dataset' used throughout various comments in this file,
#        synonymously implies the user supplied 'file upload(s)', and XML url
#        references
from brain.database.data_saver import Data_Save
from brain.converter.converter_json import JSON
from brain.session.session_base import Base
from brain.session.session_base_data import Base_Data

## Class: Data_New, inherit base methods from superclass 'Base', 'Base_Data'
class Data_New(Base, Base_Data):

  ## constructor: define class properties using the superclass 'Session_Base'
  #               constructor, along with the constructor in this subclass.
  #
  #  @super(), implement 'Session_Base' superclass constructor within this
  #      child class constructor.
  #
  #  Note: the superclass constructor expects the same 'svm_data' argument.
  def __init__(self, svm_data):
    super(Data_New, self).__init__(svm_data)
    self.observation_labels  = []

  ## save_observation_label: save the list of unique independent variable labels
  #                          from a supplied session (entity id) into the database.
  #
  #  @self.observation_labels, list of features (independent variables), defined
  #      after invoking the 'dataset_to_json' method.
  #
  #  @session_id, the corresponding returned session id from invoking the
  #      'save_svm_entity' method.
  def save_observation_label(self, session_type, session_id):
    if len(self.observation_labels) > 0:
      for label in self.observation_labels:
        db_save = Data_Save( {'label': label, 'id_entity': session_id}, 'save_label', session_type )

        # save dataset element, append error(s)
        db_return = db_save.db_data_save()
        if not db_return['status']: self.response_error.append( db_return['error'] )

  ## dataset_to_json: convert either csv, or xml dataset(s) to a uniform
  #                   json object.
  #
  #  @flag_convert, when true, indicates the file-upload mime type passed
  #      validation, and returned unique file(s) (redundancies removed).
  #
  #  @flag_append, when false, indicates the neccessary 'self.json_dataset'
  #      was not properly defined, causing this method to 'return', which
  #      essentially stops the execution of the current session.
  #
  #  @index_count, used to 'check label consistent'.
  def dataset_to_json(self, id_entity):
    flag_convert   = False
    flag_append    = True
    index_count    = 0

    try:
      self.response_mime_validation['dataset']['file_upload']
      flag_convert = True
    except Exception as error:
      self.response_error.append( error )
      print error
      return False

    if ( flag_convert ):
      self.json_dataset = []
      svm_property      = self.svm_data

      # reset file-pointer
      val['file'].seek(0)

      for val in self.response_mime_validation['dataset']['file_upload']:
        # csv to json
        if val['type'] in ('text/plain', 'text/csv'):
          try:
            # conversion
            dataset_converter = JSON(val['file'])
            dataset_converted = dataset_converter.csv_to_json()

            # check label consistency, assign labels
            if index_count > 0 and sorted(dataset_converter.get_observation_labels()) != self.observation_labels: self.response_error.append('The supplied observation labels (dependent variables), are inconsistent')
            self.observation_labels = sorted(dataset_converter.get_observation_labels())

             # build new (relevant) dataset
            self.json_dataset.append({'id_entity': id_entity, 'svm_dataset': dataset_converted})
          except Exception as error:
            self.response_error.append( error )
            flag_append = False

        # xml to json
        elif val['type'] in ('application/xml', 'text/xml' ):
          try:
            # conversion
            dataset_converter = JSON(val['file'])
            dataset_converted = dataset_converter.xml_to_json()

            # check label consistency, assign labels
            if index_count > 0 and sorted(dataset_converter.get_observation_labels()) != self.observation_labels: self.response_error.append('The supplied observation labels (dependent variables), are inconsistent')
            self.observation_labels = sorted(dataset_converter.get_observation_labels())

             # build new (relevant) dataset
            self.json_dataset.append({'id_entity': id_entity, 'svm_dataset': dataset_converted})
          except Exception as error:
            self.response_error.append( error )
            flag_append = False

      index_count += 1
      if ( flag_append == False ): return False
