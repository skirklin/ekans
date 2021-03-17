# ekans

Curses snake clone

To set up:

```
git clone git@github.com:skirklin/ekans.git
# optional, but recommended, to install packages in a local virtual environment:
python -m venv venv
source venv/bin/activate
cd ekans
pip install -U pip
pip install -r requirements.txt
pip install -e .
```

## Play yourself
```
ekans play [--level="Random(n)|Bars()|Empty()"]
```

## Run bot controller
```
ekans ai --name RandomAIController|HungryAIController [--seed=1234 --level="Random(n)|Bars()|Empty()"]
```
