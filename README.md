# HPML Research Group Publication Page Automation

This repository automates the generation of the HTML for the HPML Research Group's publication page.

## Steps

1. **Update**: Make a pull request (PR) to update the `all_publications.bib` file.  
2. **Generate**: After the PR is merged, a GitHub Action will create an updated `publications.html` file.  
3. **Publish**: Copy the `publications.html` content to the Drupal CMS to update the live page.

## Notes

- Ensure `all_publications.bib` follows the correct BibTeX format. 
- Make sure the journal/conference names align with `venue_code.yaml` 