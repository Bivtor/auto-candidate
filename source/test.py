from auto_candidate import build, HttpError, creds
import json



    


def testJobMap(job: str):
    with open('json_files/job_map.json', 'r') as f:
        # Load the JSON data from the file
        job_map = json.load(f)
        if job in job_map:
            print(job_map[job])
        else:
            print("no")
def main():
    pass
    # testJobMap('clinical director')


if __name__ == "__main__":
    main()
