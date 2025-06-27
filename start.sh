#!/bin/bash
cd backend
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH
uvicorn main:app --host 0.0.0.0 --port $PORT