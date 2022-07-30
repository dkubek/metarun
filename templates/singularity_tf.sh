#!/usr/bin/env bash
###############################################################################
#
# Example batch script for running a python tensorflow job in a singularity
# container.
#
#
# JOB ENVIRONMENT VARIABLES
#
#   JOB_COMMAND
#       Command to be executed.
#
#   JOB_RESOURCES
#       Path to the resources (files, data, scripts ...) associated with the
#       job.
#
#   JOB_OUTDIR
#       Path to the output directory of the job. Any files resulting from this
#       job should be copied here.
#
###############################################################################

# Allocate resources:
#PBS -l select=1:ncpus=24:ngpus=1:mem=16gb:scratch_local=32gb
#PBS -q gpu

#PBS -l walltime=8:00:00

# test if scratch directory is set
[[ -n "${SCRATCHDIR}" ]] || {
    echo >&2 "Variable SCRATCHDIR is not set!"
    exit 1
}

_setup() {
    export SINGULARITY_TMPDIR="${TMPDIR}"

    # Copy repository with code to be run
    rsync -r "${JOB_RESOURCES}/" "${SCRATCHDIR}" ||
        {
            echo >&2 "Error while copying input file(s)!"
            exit 2
        }

    cd "$SCRATCHDIR" || exit
}

_main() {
    # Find the newest tensorflow SIF file
    _sif_file=$(
        find /cvmfs/singularity.metacentrum.cz/NGC \
            -maxdepth 1 \
            -name "TensorFlow*-tf2-py3.SIF" \
            -printf "%T+\t%p\n" |
            sort -r |
            head -1 |
            cut -f2
    )
    singularity exec \
        --home "$SCRATCHDIR" \
        --nv \
        "${_sif_file}" \
        bash -c "${JOB_COMMAND}"
}

_teardown() {
    clean_scratch
}

_setup
_main
_teardown
