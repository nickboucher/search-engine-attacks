# Bing Chatbot

This directory contains scripts to run experiments against Bing's GPT-4 powered chatbot.

## Installation

Install node dependencies:
``sh
npm install .
``

Note that these scripts were written on Node v19.8.1.

In addition, install Python dependencies for graphing:
``sh
pip3 install -r requirements.txt
``

## Usage

To run the experiments, you must first obtain a fresh `_U` cookie from *bing.com* in a browser with a logged-in user that has access to the Bing Chatbot preview. This cookie value should then be copied into a `.env` file in this directory following the syntax given in `.env.example`.

Once this is complete, the Bing Chatbot experiments cna be launched with:
``sh
npx tsx bing-chat.ts
``

Note that the `_U` cookie currently has a TTL of 20 minutes, so if the experiment takes longer than this time a new `_U` value will need to be given and the script restarted. Further note that there is a daily query limit for the Bing chatbot, and if this limit is exceeded the experiments will need to be spread over multiple days.

Once the results have been obtained and serialized as a JSON file, they can be graphed with the following command:
``sh
./graphs.py results.json
``

The results used to create the visualizations in the associated paper are available in the `results/` subdirectory.