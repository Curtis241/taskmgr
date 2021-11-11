#!/bin/bash

source venv3/bin/activate
uvicorn taskmgr.main:app --reload
