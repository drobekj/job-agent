import requests

from sources.discovered_jobs import normalize_discovered_job


GRAPHQL_URL = "https://api.capybara.lmc.cz/api/graphql/widget"

HOST = "generaliceska.jobs.cz"
REFERER = "https://generaliceska.jobs.cz/volna-mista"
WIDGET_ID = "f737f198-f384-4aec-8ac3-c0f688e23b2d"
X_API_KEY = "f1722c10335794fb464f88f677a2f4d85ccbe55cc24a34825b47800c35f174ee"


QUERY = """
query LISTING_QUERY(
  $widgetId: ID!
  $referer: String
  $version: String
  $pageReferer: String
  $page: Int
  $gaId: String
  $lmcVisitorId: String
  $filters: [JobAdFilter!]!
  $useExampleData: Boolean!
  $host: String
  $isNotLoggableToSessionLog: Boolean
  $cookieConsent: [String]
  $matejId: String
  $rps: Int
) {
  widget(
    id: $widgetId
    referer: $referer
    pageReferer: $pageReferer
    version: $version
    lmcVisitorId: $lmcVisitorId
    gaId: $gaId
    useExampleData: $useExampleData
    host: $host
    isNotLoggableToSessionLog: $isNotLoggableToSessionLog
    cookieConsent: $cookieConsent
    matejId: $matejId
  ) {
    jobAdList(page: $page, filters: $filters, rps: $rps, isNotLoggableToSessionLog: $isNotLoggableToSessionLog) {
      groupedJobAds {
        jobAds {
          id
          title
          employer {
            companyName
          }
          locationsObjects {
            city {
              label
            }
            region {
              label
            }
            country {
              label
            }
          }
          customFields {
            name
            values {
              label
            }
          }
        }
        groups {
          jobAds {
            id
            title
            employer {
              companyName
            }
            locationsObjects {
              city {
                label
              }
              region {
                label
              }
              country {
                label
              }
            }
            customFields {
              name
              values {
                label
              }
            }
          }
        }
      }
      paginator {
        currentPage
        lastPage
        totalNumberOfItems
      }
    }
  }
}
"""


def extract_location(job_ad):
    locations = job_ad.get("locationsObjects") or []

    if not locations:
        return ""

    location = locations[0]

    city = ((location.get("city") or {}).get("label")) or ""
    region = ((location.get("region") or {}).get("label")) or ""
    country = ((location.get("country") or {}).get("label")) or ""

    return ", ".join(part for part in [city, region, country] if part)


def build_job_url(job_ad_id):
    return f"https://{HOST}/detail-pozice/?id={job_ad_id}"


def collect_job_ads(group):
    job_ads = []

    job_ads.extend(group.get("jobAds") or [])

    for subgroup in group.get("groups") or []:
        job_ads.extend(collect_job_ads(subgroup))

    return job_ads


def fetch_page(page):
    variables = {
        "version": "profi-3.23",
        "referer": REFERER,
        "pageReferer": REFERER,
        "gaId": "",
        "lmcVisitorId": "",
        "host": HOST,
        "cookieConsent": ["necessary"],
        "matejId": "",
        "widgetId": WIDGET_ID,
        "page": page,
        "useExampleData": False,
        "isNotLoggableToSessionLog": False,
        "filters": [],
        "rps": 10,
    }

    response = requests.post(
        GRAPHQL_URL,
        json={
            "query": QUERY,
            "variables": variables,
        },
        headers={
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": f"https://{HOST}",
            "Referer": f"https://{HOST}/",
            "User-Agent": "Mozilla/5.0",
            "X-Api-Key": X_API_KEY,
        },
        timeout=30,
    )

    response.raise_for_status()
    return response.json()


def discover():
    all_jobs = []
    seen_urls = set()

    page = 1
    last_page = 1

    while page <= last_page:
        data = fetch_page(page)

        job_ad_list = (
            data.get("data", {})
            .get("widget", {})
            .get("jobAdList", {})
        )

        paginator = job_ad_list.get("paginator") or {}
        last_page = paginator.get("lastPage", 1)

        grouped_job_ads = job_ad_list.get("groupedJobAds") or {}
        job_ads = collect_job_ads(grouped_job_ads)

        for job_ad in job_ads:
            job_id = job_ad.get("id")

            if not job_id:
                continue

            url = build_job_url(job_id)

            if url in seen_urls:
                continue

            seen_urls.add(url)

            employer = job_ad.get("employer") or {}

            all_jobs.append(
                normalize_discovered_job(
                    url=url,
                    source_id="generali",
                    source_type="company_career",
                    private_note="",
                    title=job_ad.get("title", ""),
                    location=extract_location(job_ad),
                    company=employer.get("companyName", "Generali Česká pojišťovna"),
                )
            )

        page += 1

    return all_jobs