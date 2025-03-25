# Helsinki ProbML Lab Publications Page Automation

This repository automates the generation of the HTML for the [Helsinki Probabilistic Machine Learning Lab](https://www.helsinki.fi/en/researchgroups/probabilistic-machine-learning) publications page, which features a list of selected publications.

## Steps

1. **Update**: Make a pull request (PR) to update the `all_publications.bib` file.  
2. **Generate**: After the PR is merged, a GitHub Action will automatically create an updated `publications.html` file.  
3. **Publish**: Copy the `publications.html` content to the Drupal CMS to update the [live page](https://www.helsinki.fi/en/researchgroups/probabilistic-machine-learning/publications).

## Notes

- Ensure `all_publications.bib` follows the correct BibTeX format. 
- Make sure the journal/conference names align with `venue_code.yaml` 
