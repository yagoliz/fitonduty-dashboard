#!/bin/bash

source ../.venv/bin/activate 
export $(cat .env | xargs)
cd .. && python3 main.py
