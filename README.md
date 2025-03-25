# Helsinki ProbML Lab Publications Page Automation

This repository automates the generation of the HTML for the [Helsinki Probabilistic Machine Learning Lab](https://www.helsinki.fi/en/researchgroups/probabilistic-machine-learning) publications page, which features a list of selected publications. The lab encompasses seven research groups at the Department of Computer Science of the University of Helsinki, all specializing in probabilistic machine learning methods and their applications.

## Steps

1. **Update**: Make a pull request (PR) to update the `all_publications.bib` file with new properly formatted bib entries.  
2. **Generate**: After the PR is merged, a GitHub Action will automatically create an updated `publications.html` file.  
3. **Publish**: Copy the `publications.html` content to the Drupal CMS to update the [live page](https://www.helsinki.fi/en/researchgroups/probabilistic-machine-learning/publications).

## Notes

- Ensure `all_publications.bib` follows the correct BibTeX format (e.g., ensure proper capitalization, all required fields, etc.). Check the existing entries for a template. 
- Make sure the journal/conference names align with `venue_code.yaml`.
- Please only add to `all_publications.bib` publications that should appear in the (selected) Publications page; there is no filtering at the moment so all bib entries will appear in the page.
