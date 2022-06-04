
pybabel init -i .\hash2passbot\apps\bot\locales\hash2passbot.pot -d .\hash2passbot\apps\bot\locales\ -D hash2passbot -l en


pybabel extract .\hash2passbot\ -o .\hash2passbot\apps\bot\locales\hash2passbot.pot

pybabel update -d .\hash2passbot\apps\bot\locales -D hash2passbot -i .\hash2passbot\apps\bot\locales\hash2passbot.pot

pybabel compile -d .\hash2passbot\apps\bot\locales\ -D hash2passbot
