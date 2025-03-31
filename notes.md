# etm as markdown files

## seeds

- Tasks with jobs
    - one markdown file with the jobs listed as 
        `- [ ]` <label>. <job name>
        - when `- [ ] <job_name>` is encountered when formatting the task, a consecutive label from a: , b: , ... is inserted before the job name
        - `- [a,b]` is interpreted as having (unfinished) prereqs corresponding to labels a and b. As these jobs are finished the prereqs are removed
        - when finished, a ✅ character is appended with completion date and the `- [ ]` is changed to `- [x]` 
