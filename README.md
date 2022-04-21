# ffmpeg-concatenate

____
This little app concatenates a list of videos into single one.

#### What *exactly* it does:

1. Reads JSON from POST request body
2. Asynchronously downloads all videos from links in JSON
3. Concatenates these videos into one using ffmpeg
4. Uploads the file to AWS s3 bucket
5. Creates a record in PostgreSQL database

#### The body for a request must look like this:
```python
{
"video_urls": string[] : required (minimum 2)
"width": int: required # width of output video
"height": int: required # height of output video
"fps": int: required # fps of output video
}
```

### Current issues:
- does not support videos without audio stream
