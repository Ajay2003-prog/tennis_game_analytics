# Tennis Game Analytics: Findings and Recommendations

## Scope and data used

This report summarizes the four existing datasets through the generated summary
CSV files and five charts:

- 6,717 competitions
- 18 competition categories
- 787 complexes
- 4,159 venues

The analysis script reads the original datasets without modifying them. The
visualization script reads only the generated summary CSV files. Percentages in
this report are calculated from those summary tables and rounded to two decimal
places.

The available data describes competitions, categories, complexes, and venues.
Competitor rankings, player records, match results, scores, and match-level
performance data are not available in the current project files.

## 1. Competition types

### Observed facts

There are 6,717 competitions in total:

| Competition type | Count | Share of competitions |
|---|---:|---:|
| Singles | 3,644 | 54.25% |
| Doubles | 3,055 | 45.48% |
| Mixed doubles | 12 | 0.18% |
| Mixed | 6 | 0.09% |

Singles are the largest type, but doubles are also a substantial part of the
dataset. Together, singles and doubles account for 6,699 competitions, or
99.73% of the total.

### Interpretation

The dataset supports a useful comparison between singles and doubles. The two
small mixed groups should remain visible, but they may need separate labels or
a smaller visual treatment so their low counts are not hidden or confused with
missing data.

## 2. Competition genders

### Observed facts

| Gender | Count | Share of competitions |
|---|---:|---:|
| Men | 3,850 | 57.32% |
| Women | 2,851 | 42.44% |
| Mixed | 16 | 0.24% |

Men's competitions exceed women's competitions by 999 records. The mixed
group is very small in this dataset.

### Interpretation

Gender is a useful dashboard filter because both men's and women's competitions
have large sample sizes. A percentage view should be shown together with the
raw count so users do not mistake the difference for a performance comparison.
This dataset measures competition records, not player quality or match results.

## 3. Competition categories

### Observed facts

The ten largest categories are:

| Category | Count | Share of competitions |
|---|---:|---:|
| ITF Men | 2,198 | 32.72% |
| ITF Women | 2,032 | 30.25% |
| Challenger | 1,071 | 15.94% |
| UTR Men | 314 | 4.67% |
| UTR Women | 264 | 3.93% |
| WTA | 261 | 3.89% |
| WTA 125K | 258 | 3.84% |
| ATP | 225 | 3.35% |
| Exhibition | 38 | 0.57% |
| Juniors | 16 | 0.24% |

These top ten categories contain 6,677 competitions, or 99.40% of all
competition records. ITF Men and ITF Women together account for 4,230 records,
or 62.97% of the dataset.

### Interpretation

The category distribution is highly concentrated in ITF and Challenger data.
This is useful for understanding the coverage of the available SportRadar
competition data, but it should not be interpreted as the global popularity or
importance of each competition level. The dashboard should make the long tail
of smaller categories accessible without allowing the largest categories to
hide them completely.

## 4. Venues by country

### Observed facts

There are 4,159 venues across 77 countries in the venue summary:

| Country | Venue count | Share of venues |
|---|---:|---:|
| USA | 702 | 16.88% |
| Italy | 302 | 7.26% |
| France | 278 | 6.68% |
| China | 243 | 5.84% |
| Spain | 217 | 5.22% |
| Germany | 182 | 4.38% |
| Mexico | 146 | 3.51% |
| Australia | 144 | 3.46% |
| England | 117 | 2.81% |
| Brazil | 113 | 2.72% |

The top ten countries contain 2,444 venues, or 58.76% of all venues. The USA
has 702 venues, more than twice the count of Italy, which has 302.

### Interpretation

Country is a strong geographic dimension for the dashboard. A country ranking,
map, or selectable country filter can help users explore where the available
venue records are concentrated. These counts describe the dataset's venue
coverage; they do not establish that the countries have more tennis activity
overall.

## 5. Venues per complex

### Observed facts

The venue summary contains 623 complexes with at least one listed venue. The
top ten complexes are:

| Complex | Venue count | Share of all venues |
|---|---:|---:|
| Buenos Aires Lawn Tennis Club | 29 | 0.70% |
| Melbourne Park | 28 | 0.67% |
| Queensland Tennis Centre | 25 | 0.60% |
| Hurd Tennis Center | 24 | 0.58% |
| AELTC Wimbledon Qualifying and Community Sports Centre | 23 | 0.55% |
| Foro Italico | 23 | 0.55% |
| Club Tennis Las Terrazas de Miraflores | 22 | 0.53% |
| Qi Zhong Tennis Center | 21 | 0.50% |
| Megasaray Tennis Academy | 21 | 0.50% |
| Indian Wells Tennis Garden | 21 | 0.50% |

The top ten complexes contain 237 venues, or 5.70% of all venues. Across the
623 complexes represented in the venue table, the mean is approximately 6.67
venues per complex.

There are 787 complexes in the complexes table, but only 623 distinct complex
IDs appear in the venue summary. Therefore, 164 complexes do not have a listed
venue in the current venue dataset. This is a data-coverage observation, not
proof that those complexes have no physical venues.

### Interpretation

The complex-to-venue relationship is useful for drill-down analysis: users can
select a complex and see how many venues are associated with it. Because the
top ten complexes represent only 5.70% of all venues, the data is not dominated
by a few complexes. The dashboard should support both a top-complex view and a
searchable full complex table.

## 6. Data-quality considerations

### Observed facts

- Every primary ID is unique in the available CSV files.
- No complete duplicate rows were found.
- `competitions.parent_id` is missing for 623 competition records.
- Repeated `category_id`, `parent_id`, and `complex_id` values are foreign-key
  relationships and were not treated as duplicate records.

### Interpretation

The primary keys are suitable for counting records without double-counting
duplicate entities. The missing parent IDs should be represented as `No parent`
or `Unknown` in any parent-competition filter rather than silently removed.

## 7. Recommendations for the planned dashboard

1. Add headline metrics for total competitions (`6,717`), total venues
   (`4,159`), total categories (`18`), and total complexes (`787`).
2. Add filters for competition type, gender, category, country, and complex.
3. Show both counts and percentages for type, gender, category, and country
   summaries.
4. Use a top-10 chart for categories, countries, and complexes, with a
   searchable table for the complete results.
5. Include a `No parent` option for the 623 competitions with missing
   `parent_id` values.
6. Keep venue counts separate from competition counts so users do not compare
   the two measures as if they represented the same unit.
7. Add a note that the current dashboard contains no competitor rankings or
   match results. Those features require additional API data from the team.

## 8. Limitations and next data requirement

The current analysis is descriptive. It identifies how records are distributed
by competition and location fields, but it cannot measure player performance,
rankings, wins, losses, scores, or match-level trends.

To add competitor-ranking or match-result analysis, the team must provide the
corresponding SportRadar API endpoints or exported datasets, including stable
competitor IDs, ranking dates or match dates, and the relevant ranking or match
fields. No rankings or results have been invented in this report.
