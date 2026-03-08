class OSINTSkills:
    @staticmethod
    def get_skill_tree():
        return """
# OSINT SKILL TREE (Kali Linux)
When you are assigned an OSINT task, follow this progression from top to bottom. Do not jump to Level 3 or 4 before exhausting possibilities in Level 1.

## LEVEL 1: Passive Reconnaissance (Identifier Search & Footprinting)
- **Names / Usernames**: `sherlock <username> --timeout 10`
- **Email Harvesting**: `theHarvester -d <domain> -l 500 -b all` or `h8mail -t <target>`
- **Domain Info**: `whois <domain>`, `dnsrecon -d <domain>`

## LEVEL 2: Active Scanning (Network & Infrastructure Mapping)
- **Port/Service Scanning**: `nmap -sS -A -T4 -p- <ip>`
- **Subdomain Enumeration**: `amass enum -d <domain>`
- **Web App Crawling**: `dirb http://<target>/`

## LEVEL 3: Vulnerability Scanning (Nuclei & Deep Analysis)
- **Zero-days/Exposures**: Use `run_nuclei` against the target to automate vulnerability discovery. 
- **Web Vulnerabilities**: `nikto -h http://<target>`
- **Database/SQLi check**: `sqlmap -u "http://<target>/page.php?id=1" --batch`
- **Metadata Extraction**: Use `wget` to download images/documents and run `exiftool <file>` to extract metadata.

## LEVEL 4: Correlation & Conclusion (LLM Task)
- Review outputs from Levels 1-3.
- Identify relationships: Does a recovered email correlate to a username found in sherlock?
- Formulate an actionable report outlining findings, potential vulnerabilities, and intelligence.
"""
