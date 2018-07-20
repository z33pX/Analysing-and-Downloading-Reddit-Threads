This script downloads a certain number of threads of a certain topic from the Reddit forum.

Usage
-

```
if __name__ == '__main__':
    reddit_search(
        keyword="algotrading",
        numer_of_threads=1,
        dump_to_json="database.json",
        append=False)
```
- `keyword`: Keyword
- `numer_of_threads`: Number of threads you want to load maximum
- `dump_to_json`: Dumps the complete thread plus entity analysis to a json file
- `append`: If True, the results will be appended to the json file.
