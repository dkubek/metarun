# ``metarun``
A small script for running (possibly) multiple parallel jobs on MetaCentrum.

## Installation

The only dependencies are ``bash``, ``ssh`` for remote access and ``rsync`` for
copying of files.

To install the script simply copy the ``mrun`` script to your path.

## Features

TODO

## Usage

To create a job you first need to create a ``Mrunfile``. This file contains the description of the job (what files to copy, the command to execute on the remote etc.). The ``Mrunfile`` is a simple collection of bash variables that is later sourced into the script.

The supported parameters are:
 - **job_name** : the name of the job. By default the name of the parent directory of the ``Mrunfile`` will be used.

 - **data** : an array of files to copy to the remote. Note that the paths to files should be given relative to the ``Mrunfile``

 - **batch_script** : path to the batch script that will be executed on the frontend (default: ``${job_name}.sh``)

 - **job_command** : can be either a single string or an array of strings representing commands to be executed. Note that by default all commands will be executed in parallel.

Note that one can override these option using command line arguments (see  ``mrun help run``).

For an example of an ``Mrunfile`` see the ``examples/`` folder.

The job is then run using the ``run`` subcommand. It looks for a ``Mrunfile`` in the current working directory (additionally a path to the ``Mrunfile`` can be specified using the ``-f`` option).
```bash
# Note: Mrunfile exists in the cwd
mrun run <uname>@<frontend> run
```
The above command runs the job on the specified frontend. Note that it is possible to use hosts configured in the ssh ``config`` file.

When a job is run, all the required files are copied to the remote frontend to a ``jobs/`` directory in the home of the user. Each job lives in it's own subdirectory.

```
jobs
├── job01
│   ├── data/       # Files for job01
│   ├── out/        # Output of runs of job1
|   └── job01.sh    # Batch script for job01
├── job02
│   ├── data/       # Files for job02
│   ├── out/        # Output of runs of job2
|   └── job02.sh    # Batch script for job02
| ...
```

Firstly all the required files are copied to the ``data`` folder for the job. Note that the files are only updated with subsequent runs of the ``mrun`` command. To push only push files to the remote, use the ``-P`` option or the ``mrun push`` subcommand.

After all the files are copied a batch script is run for every subcommand.
When the batch script is run a number of additional variables is available in the environment:

 - **JOB_COMMAND** : Command to be executed.

 - **JOB_RESOURCES** : Path to the resources (files, data, scripts ...) associated with the job.

 - **JOB_OUTDIR** : Path to the output directory of the job. Any files resulting from this job should be copied here.

To see an example of a batch script using these variables see the ``templates/`` directory.