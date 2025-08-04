import wikipedia
import re
from typing import Optional, List

# Configure default language (you can adjust this as needed)
wikipedia.set_lang("en")

def _try_title_variants(title: str, original_title: Optional[str], year: Optional[int]) -> List[str]:
    """Generate likely Wikipedia page titles for a given movie"""
    title_variants = []

    if year:
        title_variants.append(f"{title} ({year} film)")
    title_variants.append(f"{title} (film)")
    title_variants.append(title)

    if original_title and original_title != title:
        if year:
            title_variants.append(f"{original_title} ({year} film)")
        title_variants.append(f"{original_title} (film)")
        title_variants.append(original_title)

    return title_variants


def _extract_plot_section(text: str) -> Optional[str]:
    """Extract the 'Plot' section from the Wikipedia article text using regex"""
    # Normalize line endings and remove infobox artifacts
    cleaned = text.replace('\r', '')

    # Match any header that looks like "== Plot ==" or "== Synopsis =="
    match = re.search(r"==\s*(Plot|Synopsis)\s*==\s*(.*?)\s*(==|$)", cleaned, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(2).strip()
    return None


def get_movie_plot(title: str, year: Optional[int] = None, original_title: Optional[str] = None) -> Optional[str]:
    """
    Tries to find the plot of a movie from Wikipedia using title and optionally year/original_title.
    Returns a cleaned plot string or None if not found.
    """
    title_variants = _try_title_variants(title, original_title, year)

    for variant in title_variants:
        try:
            print(f"[Wikipedia] Trying: {variant}")
            page = wikipedia.page(variant, auto_suggest=False)
            plot = _extract_plot_section(page.content)

            if plot:
                print(f"[Wikipedia] Found plot for {variant}")
                return plot
            else:
                print(f"[Wikipedia] No plot section found for {variant}")
        except wikipedia.exceptions.DisambiguationError as e:
            print(f"[Wikipedia] Disambiguation error for '{variant}': {e.options[:3]}")
            continue
        except wikipedia.exceptions.PageError:
            print(f"[Wikipedia] Page not found: {variant}")
            continue
        except Exception as e:
            print(f"[Wikipedia] Unexpected error for {variant}: {e}")
            continue

    print("[Wikipedia] No plot found for any variant.")
    return None
