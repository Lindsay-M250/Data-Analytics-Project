# AI Usage Declaration

Tool: Claude (Anthropic), model Claude Sonnet 5.5 (claude-sonnet-5-5), default settings. Effort: [fill in].

## Lindsay

| Task | What I asked (summary) | What the AI produced | What I did myself |
|---|---|---|---|
| Question 1: spread of GDP per head | How to measure whether the gap between regions narrows | Python code for the spread (standard deviation of log GDP per head), three samples, tables and chart | Ran it on our data and compared the output |
| Question 1: interpretation | Refine my draft text | Reworded paragraphs, check for Romania's effect | Checked every number against the code output and edited the text |
| Question 1: robustness | Check without big cities, from 2003 and in euro | Code for the three checks | Ran it on our raw GDP file and read the results |
| Project documents | README and report structure | Drafts | Edited them; content decided by the group |

Checking: I ran all code myself and compared the numbers in the text with the output. The AI made mistakes that I corrected (for example, wrong claims about region counts and timing), so the code output decided what stayed in the report.

## Bhongolethu


## Winnie

| Task | What I asked (summary) | What the AI produced | What I did myself |
|---|---|---|---|
| Youth data: ages 15-24 and 15-29 | How to make one clean file per age group from the raw unemployment file, with the team's cleaning rules | A script (`youth_age_groups.py`) copied from the team's cleaning code; only the age group differs | Ran it and checked that the 15-24 file is identical to `youth.csv` |
| Question 4: both tests on youth data | Step-by-step help to apply the Question 1 and 2 methods to the youth data and compare the two age groups | Python code, tables, charts and an explanation of each step | Ran every chunk in Positron and compared my output with the expected numbers |
| Question 4: where the two tests disagree | How to put the spread test and the catching-up test side by side for GDP, employment and youth | Code for the comparison table and chart, and a draft of the report text | Read every paragraph and rewrote the text in my own words |
| Setup | Python and Quarto errors on my laptop | Step-by-step fixes | Ran them and sent screenshots |

Checking: I ran all code myself and compared the numbers in the text with the output. The AI corrected two of its own statements after checking the data: the dots at the bottom right of the catching-up chart are mostly southern Italian regions (not Polish, Czech or Slovak), and the 2005 drop in the youth spread is not explained by new regions joining the sample.