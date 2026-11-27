# The bug hunt: `splitbill`

`splitbill` splits a restaurant bill between friends. It's the practice
project for [Lesson 09: Opening a good issue](../lessons/09-opening-an-issue/).

**It has bugs on purpose.** This page says how `splitbill` *should*
behave. Wherever the program does something different, you've found a bug.
Find one, then report it with the **Bug hunt** issue form. A bot checks your
report and a maintainer reviews it, then closes it: the bugs stay, so a
closed report means reviewed, not rejected.

Please don't open a pull request that fixes the bugs: the next learner
needs them.

## Running it

From the course folder (Python 3.12 or newer, nothing to install):

```bash
python bug-hunt/splitbill.py 120 --people 4 --tip 15
```

```text
Bill:  $120.00
Tax:   $0.00
Tip:   $18.00 (15%)
Total: $138.00

Person 1: $34.50
Person 2: $34.50
Person 3: $34.50
Person 4: $34.50
```

## How it should behave

```text
splitbill BILL [--people N] [--tip PERCENT] [--tax AMOUNT]
```

- **`BILL`** is the bill before tax and tip, like `120` or `120.50`.
- **`--people N`** is how many people share the bill. The default is 1.
  It must be at least 1; anything else prints
  `splitbill: error: --people must be at least 1` and exits with status 2,
  like any other bad option.
- **`--tip PERCENT`** is the tip, as a percentage. `--tip 15` and
  `--tip 15%` mean the same thing. The default is no tip.
- **`--tax AMOUNT`** is the tax, as an amount of money, like `--tax 9.60`.
  The default is no tax.
- **The tip is worked out on the bill before tax.** With a $100 bill,
  $10 of tax and a 20% tip, the tip is $20.00 and the total is $130.00.
- **The shares always add up to the total, to the cent.** When the total
  doesn't divide evenly, the first people pay one cent more: $100 split 3
  ways is $33.34, $33.33 and $33.33.
- **Money is shown with two decimals and thousands separators**, like
  `$1,234.50`.
- **`--version`** prints the version, like `splitbill 1.2.0`.

## Tests

```bash
python -m pytest bug-hunt
```

They all pass. Passing tests don't mean there are no bugs: they only check
what someone thought to test.
