# baseEEG
Lab-wide EEG scripts

If working on development for this project, please use the docker image located at `base_eeg_docker_files/`. Directions on installation and usage located in `base_eeg_docker_files/README.md`. 


## Issues

See issues for current/future work. 

Always assign yourself to an issue before beginning work on it!

If someone is already assigned to an issue, but you want to help, post a comment to ask if you can help before assigning yourself. If no response within 24 hours, then you are free to start work on the issue, but post another comment first to let them know what you will be doing.


## Git Workflow 

![ndcworkflow](https://user-images.githubusercontent.com/26397102/116148813-00512800-a6a7-11eb-9624-cd81f11d3ada.png)


Folder/branch organization should follow this convention:

`main`
- no test features
- 100% stable and usable by any lab members 
- *no direct commits*

`->dev`
- Up to date development branch with properly tested/reviewed features 
- *no direct commits*

`-->dev-feature-[featureName]`
- Ongoing development and testing of feature to be pull requested into `dev` 
- *no direct commits*

`--->dev-feature-[featureName]-[yourName]`
- *only* branch available for personal development, must be branched off of `-->dev-feature-[featureName]` branch
- Merged into `-->dev-feature-[featureName]` after pull-request (code review)


## Reminders
1. only push directly (without code review) to dev-feature-[featureName]=[yourName]
2. Must initiate pull request (and assign at least one person) for any higher-level branch
3. Mandatory code review by one person for all pull requests 


## CI test
NDCLab CI test documentation: https://docs.google.com/document/d/1lTYCLn6XK4Ln-BjcNhMMqpQFhYWg6OHB/edit


## Example File for Development
- [BIDS.zip](https://drive.google.com/drive/u/0/folders/1aQY97T9EfkPEkuiCav2ei9cs0DFegO4-) is used as input file for all pipeline features.


## Roadmap

All features (pipeline steps) can and should be worked on independently and in parallel. Any steps for which implementation relied on a prior step first being completed have been merged into one single feature (e.g., feature-ica contains three steps that must be implemented sequentially). Please self-assign to any feature, read the relevant documentation, reach out with questions, and begin implementation. There is no correct order to implement any of these steps.

The Preprocessing pipeline assumes that data is already in BIDS format. Thus, any scripts (e.g. feature-filter-io) to convert data to BIDS format are NOT part of the preprocessing pipeline. Thus, all steps of the preprocessing pipeline should be written in such a way as to assume a BIDS folder structure file already exists and that standard BIDS metadata files exist (which can be read in to govern preprocessing). Moreover, all outputs of the preprocessing stream should either be in line with existing BIDS standards or if they relate to a feature that there is not yet a BIDS standard for, the developer should set things up in a way that is in line with general BIDS principles.


### Input/Output .json and .log files

Given that the final pipeline will read from a user-supplied json file called "user_params.json" and write to an annotations file called "annotations_preproc.json", all independent feature development should refer to a common standard format for these two files to allow for easier integration of features for the final pipeline. In addition to the "annotations_preproc.json" output file, all features should all provide more verbose writing of outputs to an output.log file.

The "user_params.json" should control all research-relevant features of the pipeline (e.g. filter cutoffs, segmentation lengths, etc.). The "annotations_preproc.json" output file should contain all research-relevant outputs of the pipeline (e.g. # bad channels rejected, # ICA artifacts rejected, etc.). Together, the contents of "user_params.json" "annotations_preproc.json" should define all details neccesary to write relevant methods and results section for a journal publication to describe what the preprocessing pipeline did and what the outputs were. In fact, the long term goal is to automate the writing of these journal article sections via a script that takes "user_params.json" and "annotations_preproc.json" as inputs. In contrast, the output.log file reflects a much more verbose record of what was run, what the outputs were, and the pressence of any warning/errors, etc. 


### user_params.json

This input file will define a set of function parameter constants. The user may define these paremeters within the JSON file to infuence filtering and channel rejection. 

(please add additional fields as necessary; do not hesitate to add fields. Basically, when working on a feature, if you think there is a parameter that users might want to control, just add another field to the "user_params.json" file. There is no issue with having lots of fields with default values.)

Format:
```javascript
{
    "highPass": [.3],
    "lowpass": [50]
}
```

### annotations_preproc.json

This output file will define which EEG data-set attributes were removed or transformed through the pipeline. This file will be built iteratively as the pipeline progresses. 

(please add additional fields as necessary; do not hesitate to add fields. Basically, when working on a feature, if you think there is a value that is computed that might be of use to users, please add it to the "annotations_preproc.json" file.)

Format:
```javascript
{
    "globalBad_Chans": [1, 23, 119],
    "icArtifacts": [1, 3, 9]
}
```

### output.log

This output file will define the verbose outputs of mne functions including warnings and errors. Format will vary based on pipeline output.

To record function output to log-file, insert the following:
```python 
# initialize log-file
logging.basicConfig(filename='output.log', filemode='a', encoding='utf-8', level=logging.NOTSET)

# ... pipeline steps execute ...

logging.info("describe output of pipeline")
# record pipeline output
logging.info(mne.post.info)
```
### Steps/features of the pipline:

- Feature-filter
-High pass filter the data using mne function
-Read in the the "highPass" "lowpass" fields from the "user_params.json" file to define filter parameters

- Feature-badchans
-auto-detect and remove bad channels (those that are “noisy” for a majority of the recording)
-write to annotations file to indicate which channels were detected as bad (write to field "globalBad_chans")

- Feature-ica
This feature includes three main (and sequential) steps: 1. Prepica; 2. Ica; 3. Rejica
Overview: ICA requires a decent amount of stationarity in the data. This is often violated by raw EEG. One way around this is to first make a copy of the eeg data. For the copy, use automated methods to detect noisy portions of data and remove these sections of data. Run ICA on the copied data after cleaning. Finally, take the ICA weights produced by the copied dataset and copy them back to the recording prior to making a copy (and prior to removing sections of noisy data). In this way, we do not have to “throw out” sections of noisy data, while at the same time, we are able to derive an improved ICA decomposition.
Prepica
-Make a copy of the eeg recording
-For the copied data: high-pass filter at 1 hz
-For the copied data: segment/epoch (“cut”) the continuous EEG recording into arbitrary 1-second epochs
-For the copied data: Use automated methods (voltage outlier detection and spectral outlier detection) to detect epochs -that are excessively “noisy” for any channel
-For the copied data: reject (remove) the noisy periods of data
-Write to the annotations file which segments were rejected and based on what metrics
Ica
-For the copied data: run ica
-Copy the ica weights from the copied data back to the data pre-copy
Rejica
-Using automated methods (TBD) identify ica components that reflect artifacts
-Remove the data corresponding to the ica-identified-artifacts
-Write to the annotations file which ica components were identified as artifacts in the "icArtifacts" field

- Feature-segment
-segment/epoch (cut) the continuous data into epochs of data, such that the zero point for each epoch is a given marker of interest
-write to annotations file which markers were used for epoching purposes, how many of each epoch were created, and how many ms appear before/after the markers of interest

- Feature-finalrej
-loop through each channel. For a given channel, loop over all epochs for that channel and identify epochs for which that channel, for a given epoch, exceeds either the voltage threshold or spectral threshold. If it exceeds the threshold, reject the channel data for this channel/epoch.
-write to the annotations file which channel/epoch intersections were rejected

- Feature-interp
-interpolate missing channels, at the channel/epoch level using a spherical spline interpolation, as implemented in mne
-interpolate missing channels, at the global level, using a spherical spline interpolation, as implemented in mne
-write to annotations file which channels were interpolated and using what method

- Feature-reref
-re-reference the data to the average of all electrodes (“average reference”) using the mne function
-write to annotations file that data were re-referenced to average

