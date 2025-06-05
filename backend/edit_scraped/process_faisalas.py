import re
import os
import json
import time

# --- Regular Expression Patterns (Final Refined Version) ---

unique_id_base_pattern = re.compile(r"^(निर्णय नं\.\s*[\u0966-\u096F\u09E6-\u09EF]+)")
faisala_miti_pattern = re.compile(
    r"फैसला मिति\s*:\s*([\u0966-\u096F\u09E6-\u09EF०-९]{4}[/\-\.][\u0966-\u096F\u09E6-\u09EF०-९]{1,2}[/\-\.][\u0966-\u096F\u09E6-\u09EF०-९]{1,2})"
)
judges_pattern = re.compile(r"माननीय\s+([^\n]+)")
current_decision_metadata_block_pattern = re.compile(
    r"^(?:[\s\S]*?)"
    r"(?:\n(?:फैसला मिति|आदेश मिति)\s*:\s*[\u0966-\u096F\u09E6-\u09EF०-९]{4}[/\-\.][\u0966-\u096F\u09E6-\u09EF०-९]{1,2}[/\-\.][\u0966-\u096F\u09E6-\u09EF०-९]{1,2}\s*\n"
    r"[०-९\u0966-\u096F\u09E6-\u09EF\s\-CRCIOWS.]+\n)"
)
pakshya_pattern = re.compile(
    r"^(?:रिट निवेदक|निवेदक|पुनरावेदक\s*/\s*(?:प्रतिवादी|वादी))\s*:\s*([\s\S]*?)(?=\n\s*विरूद्ध|\n\s*विपक्षी\s*:|\n{2,})",
    re.MULTILINE
)
bipakshya_pattern = re.compile(
    r"^(?:विरूद्ध\n?(?:प्रत्यर्थी\s*/\s*(?:वादी|प्रतिवादी)\s*:\s*)?|विपक्षी\s*:\s*)([\s\S]*?)"
    r"(?=\n{2,}\S|\n\s*(?:(?:पुनरावेदक(?: / (?:वादी|प्रतिवादी))?|निवेदक|विपक्षी|प्रत्यर्थी)(?:को|का)? तर्फबाट|अवलम्बित नजिर|सम्बद्ध कानून|फैसला|आदेश|\(प्रकरण नं\.|$))",
    re.MULTILINE
)

pakshya_adhibakta_pattern = re.compile(
    r"^(?:वादी(?:को|का)? तर्फबाट|निवेदक(?:को|का)? तर्फबाट|पुनरावेदक\s*/\s*(?:प्रतिवादी|वादी)(?:को|का)? तर्फबाट)\s*:\s*([\s\S]*?)"  # Added 'वादी' here
    r"(?=\n\s*(?:प्रतिवादी(?:को|का)? तर्फबाट|विपक्षी(?:को|का|बाट)? तर्फबाट|प्रत्यर्थी\s*/\s*(?:वादी|प्रतिवादी)(?:को|का)? तर्फबाट)|\n{2,}|अवलम्बित नजिर\s*:|सम्बद्ध कानून\s*:|फैसला|$)", # Added 'प्रतिवादी' to the lookahead
    re.MULTILINE
)
bipakshya_adhibakta_pattern = re.compile(
    r"^(?:विपक्षी(?:को|का|बाट)? तर्फबाट|प्रत्यर्थी\s*/\s*(?:वादी|प्रतिवादी)(?:को|का)? तर्फबाट)\s*:\s*([\s\S]*?)"
    r"(?=\n{2,}|अवलम्बित नजिर\s*:|सम्बद्ध कानून\s*:|फैसला|आदेश|\(प्रकरण नं\.|$)",
    re.MULTILINE
)
abalambit_najir_pattern = re.compile(
    r"^अवलम्बित नजिर\s*:([\s\S]*?)"
    r"(?=\n\s*सम्बद्ध कानून\s*:|^\s*(?:सुरू|जिल्ला अदालतमा|उच्च अदालतमा) फैसला गर्ने|$)",
    re.MULTILINE
)
sambaddha_kanoon_pattern = re.compile(
    r"^सम्बद्ध कानून\s*:\s*([\s\S]*?)"
    r"(?=\n{2,}|^\s*(?:सुरू(?: तहमा)?|जिल्ला अदालतमा|उच्च अदालतमा) फैसला गर्ने(?:ः-)?|^\s*फैसला\s*\n|^\s*आदेश\s*\n|$)",
    re.MULTILINE
)
ullikhit_najir_pattern = re.compile(
    r"((?:(?:ने\.(?:का\.)?प\.?)|निकाप|स\.अ\.बुलेटिन|ऐ\.।\s*ऐ\.।)(?:,\s*[\u0966-\u096F\u09E6-\u09EF०-९\s\/\-\u0900-\u097F]{1,200}?)(?:(?:नि\.नं\.|पृ\.)\s*[\u0966-\u096F\u09E6-\u09EF०-९]+))"
    r"|((?:(?:ने\.(?:का\.)?प\.?)|निकाप|स\.अ\.बुलेटिन|ऐ\.)\s*[\u0966-\u096F\u09E6-\u09EF]{4}(?:\s*को|,\s*अङ्क)?(?:[\s\S]{1,200}?)(?:नि\.नं\.|पृ\.)\s*[\u0966-\u096F\u09E6-\u09EF०-९]+)"
    r"|(?:नेकाप\s*[\u0966-\u096F\u09E6-\u09EF]{4}(?:\s+[\u0900-\u097F]+को)?\s*(?:पृष्ठ|नि\.नं\.)\s*[\u0966-\u096F\u09E6-\u09EF०-९]+)"
)

# --- Components for ullikhit_kanoon_pattern (Precise pattern for use on short sentences) ---
_sdt_strict = r"[\u0966-\u096F\u09E6-\u09EF०-९क-ज्ञ\(\)\.\-नं]+"
_sdt_list_strict = _sdt_strict + r"(?:\s*(?:,|र|तथा)\s*" + _sdt_strict + r")*"
_law_core_name_simplified = r"(?:[\u0900-\u097F]+(?:(?:\s+|\.)[\u0900-\u097F]+){0,5})"
_law_type_simplified = r"(?:ऐन|संहिता|संविधान|नियमावली|नियम|महासन्धि|आदेश|कानून|बन्दोबस्त|ऐ\.ऐन|ऐनको)"
_year_simplified = r"(?:\s*,\s*[\u0966-\u096F\u09E6-\u09EF]{4})?"
_connector_simplified = r"(?:\s*को|\s+सम्बन्धी|\s*अन्तर्गत|\s*बमोजिम)?"
_section_keyword_simplified = r"(?:दफा|धारा|अनुच्छेद|महलको?|नियम|उपदफा|खण्ड|नं\.?|नम्बर|परिच्छेद|बूँदा|देहाय)"
_p1_simple = (_law_core_name_simplified + r"\s*" + _law_type_simplified + _year_simplified + _connector_simplified + r"\s*" + _section_keyword_simplified + r"\s*" + _sdt_list_strict + r"(?:\s*को\s*(?:खण्ड|देहाय)\s*" + _sdt_strict + r")*")
_p2_simple = (_law_type_simplified + _connector_simplified + r"\s*" + _section_keyword_simplified + r"\s*" + _sdt_list_strict + r"(?:\s*को\s*(?:खण्ड|देहाय)\s*" + _sdt_strict + r")*")
_p3_simple = r"(?:मुलुकी\sऐन(?:,\s*" + _law_core_name_simplified + r")?\s*को\s*महलको\s*" + _sdt_list_strict + ")"
_p4_simple = r"(?:अ\.बं\.\s*[\u0966-\u096F\u09E6-\u09EF०-९]+(?:[क-ज्ञ]?\s*नं\.?)?)"
# This is the precise (but potentially slow) pattern we will use on SHORT sentences only.
precise_kanoon_pattern_for_sentence = re.compile(f"({_p1_simple}|{_p2_simple}|{_p3_simple}|{_p4_simple})")


# --- Helper Functions ---
def extract_with_regex(pattern, text, field_name_for_debug="field", multi=False, group_index=1, clean_func=None, default_val_single="NA", default_val_multi=None):
    if default_val_multi is None: default_val_multi = []
    if text is None: return default_val_multi if multi else default_val_single
    try:
        matches = pattern.findall(text)
        if multi:
            if not matches: return default_val_multi
            if isinstance(matches[0], tuple): results = [m[group_index-1] for m in matches if len(m) >= group_index and m[group_index-1]]
            else: results = [m for m in matches if m]
            cleaned_results = list(set(clean_func(item) for item in results if item and clean_func(item))) if clean_func else list(set(str(item).strip() for item in results if item and str(item).strip()))
            return cleaned_results if cleaned_results else default_val_multi
        elif matches:
            result = matches[0]
            if isinstance(result, tuple): result_to_clean = result[group_index-1] if len(result) >= group_index and result[group_index-1] else (result[0] if result and result[0] else None)
            else: result_to_clean = result
            cleaned_result = clean_func(result_to_clean) if clean_func and result_to_clean else (str(result_to_clean).strip() if result_to_clean else None)
            return cleaned_result if cleaned_result else default_val_single
    except Exception as e: print(f"ERROR during regex extraction for '{field_name_for_debug}': {e}")
    return default_val_multi if multi else default_val_single

# NEW TWO-STAGE FUNCTION for fast and accurate implicit kanoon extraction
def extract_implicit_kanoon_fast(detail_text):
    if not detail_text:
        return []

    # 1. Define keywords that are strong indicators of a law citation.
    keywords = ["ऐन", "संविधान", "संहिता", "नियमावली", "नियम", "महासन्धि", "आदेश", "कानून", "बन्दोबस्त", "अ.बं."]
    
    # 2. Split the text into smaller, more manageable chunks (e.g., sentences).
    sentences = re.split(r'[।\n]', detail_text)
    
    potential_citations = []
    
    # 3. For each sentence, check if it contains a keyword.
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Quick check for any keyword
        if any(kw in sentence for kw in keywords):
            # 4. If a keyword is found, apply our precise (but slow on large text) regex
            # to this short sentence to extract the full citation phrase.
            matches = precise_kanoon_pattern_for_sentence.finditer(sentence)
            for match in matches:
                # No need to do the '।' trimming here since we already split by it.
                potential_citations.append(match.group(0).strip())

    return list(set(potential_citations))


def clean_multiline_text(text_input):
    if not text_input or text_input == DEFAULT_STRING: return text_input
    text_input_str = str(text_input).strip(); lines = [line.strip() for line in text_input_str.split('\n') if line.strip()]
    cleaned_text = "\n".join(lines)
    return cleaned_text if cleaned_text else None

def clean_singleline_text(text_input):
    if not text_input or text_input == DEFAULT_STRING: return text_input
    cleaned = str(text_input).strip()
    return cleaned if cleaned else None

# --- Configuration ---
SOURCE_DIR = '../scraped_articles' # Adjust this path as needed
OUTPUT_DIR = 'edited_faisalas' # Changed output dir to avoid overwriting
DEFAULT_STRING = "NA"
DEFAULT_LIST = []

# --- Main Processing Logic ---
def process_faisalas():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    processed_files = 0; total_files = len([name for name in os.listdir(SOURCE_DIR) if name.endswith('.json')]); current_file_num = 0

    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith('.json'):
            current_file_num += 1; filepath = os.path.join(SOURCE_DIR, filename)
            output_filepath = os.path.join(OUTPUT_DIR, filename)
            print(f"\nProcessing file {current_file_num}/{total_files}: {filename}...")
            start_time = time.time()
            with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)

            current_extracted_values = {}
            title = data.get("Title"); post_meta = data.get("Post Meta"); faisala_detail_raw = data.get("Faisala Detail")

            if title:
                match = unique_id_base_pattern.search(title)
                if match: current_extracted_values["uniqueId"] = match.group(1).replace("निर्णय", "नि.")
            current_extracted_values["faisala_miti"] = extract_with_regex(faisala_miti_pattern, post_meta, "faisala_miti", clean_func=clean_singleline_text)
            
            if faisala_detail_raw:
                # Judge extraction logic...
                judge_extraction_block = faisala_detail_raw; judge_block_match = current_decision_metadata_block_pattern.search(faisala_detail_raw)
                if judge_block_match:
                    potential_block = faisala_detail_raw[:judge_block_match.start()]
                    first_faisala_miti_in_block = re.search(r"\n(?:फैसला मिति|आदेश मिति)\s*:", potential_block)
                    if first_faisala_miti_in_block: judge_extraction_block = potential_block[:first_faisala_miti_in_block.start()]
                    else: judge_extraction_block = potential_block
                else:
                    lines = faisala_detail_raw.split('\n'); limit = 7
                    for i, line in enumerate(lines[:12]):
                        if line.strip().startswith(("मुद्दा :", "विषयः")) or \
                           (line.strip().startswith(("फैसला मिति :", "आदेश मिति :")) and i > 0 and \
                            i + 1 < len(lines) and re.match(r"^[०-९\u0966-\u096F\u09E6-\u09EF\s\-CRCIOWS.]+$", lines[i+1].strip())):
                            limit = i; break
                    judge_extraction_block = "\n".join(lines[:limit])
                
                # Main extractions
                current_extracted_values["judges"] = extract_with_regex(judges_pattern, judge_extraction_block, "judges", multi=True, clean_func=clean_singleline_text)
                current_extracted_values["pakshya"] = extract_with_regex(pakshya_pattern, faisala_detail_raw, "pakshya", clean_func=clean_multiline_text)
                current_extracted_values["bipakshya"] = extract_with_regex(bipakshya_pattern, faisala_detail_raw, "bipakshya", clean_func=clean_multiline_text)
                current_extracted_values["pakshya_adhibakta"] = extract_with_regex(pakshya_adhibakta_pattern, faisala_detail_raw, "pakshya_adhibakta", clean_func=clean_multiline_text)
                current_extracted_values["bipakshya_adhibakta"] = extract_with_regex(bipakshya_adhibakta_pattern, faisala_detail_raw, "bipakshya_adhibakta", clean_func=clean_multiline_text)
                current_extracted_values["abalambit_najir_explicit"] = extract_with_regex(abalambit_najir_pattern, faisala_detail_raw, "abalambit_najir_explicit", clean_func=clean_multiline_text)
                current_extracted_values["sambaddha_kanoon_explicit"] = extract_with_regex(sambaddha_kanoon_pattern, faisala_detail_raw, "sambaddha_kanoon_explicit", clean_func=clean_multiline_text)
                
                raw_najir_matches = ullikhit_najir_pattern.finditer(faisala_detail_raw)
                temp_najir_list = [match.group(0).strip() for match in raw_najir_matches if match.group(0)]
                current_extracted_values["ullikhit_najir_implicit"] = list(set(clean_singleline_text(n) for n in temp_najir_list if clean_singleline_text(n)))

                # *** NEW TWO-STAGE METHOD FOR IMPLICIT KANOON ***
                current_extracted_values["ullikhit_kanoon_implicit"] = extract_implicit_kanoon_fast(faisala_detail_raw)

            # Assemble final output with defaults
            output_payload_with_defaults = {
                "uniqueId": DEFAULT_STRING, "faisala_miti": DEFAULT_STRING, "judges": DEFAULT_LIST[:],
                "pakshya": DEFAULT_STRING, "bipakshya": DEFAULT_STRING, "pakshya_adhibakta": DEFAULT_STRING,
                "bipakshya_adhibakta": DEFAULT_STRING, "abalambit_najir_explicit": DEFAULT_STRING,
                "sambaddha_kanoon_explicit": DEFAULT_STRING, "ullikhit_najir_implicit": DEFAULT_LIST[:],
                "ullikhit_kanoon_implicit": DEFAULT_LIST[:],
            }
            for key, val in current_extracted_values.items():
                if isinstance(val, list):
                    if val: output_payload_with_defaults[key] = val
                elif isinstance(val, str) and val.strip() and val != DEFAULT_STRING:
                    output_payload_with_defaults[key] = val
                elif val is not None and not isinstance(val, (str, list)):
                    output_payload_with_defaults[key] = val
            
            output_data_payload = data.copy()
            output_data_payload.update(output_payload_with_defaults)
            if "Faisala Detail" in output_data_payload and faisala_detail_raw is not None:
                output_data_payload["Faisala_Detail_raw_text"] = faisala_detail_raw
                if "Faisala Detail" in output_data_payload: del output_data_payload["Faisala Detail"]
            elif "Faisala Detail" in output_data_payload : del output_data_payload["Faisala Detail"]

            with open(output_filepath, 'w', encoding='utf-8') as f_out: json.dump(output_data_payload, f_out, ensure_ascii=False, indent=4)
            end_time = time.time()
            print(f"  Successfully processed and saved: {output_filepath} (took {end_time - start_time:.2f}s)")
            processed_files += 1
    print(f"\n--- Processing Complete ---\nTotal files processed: {processed_files}")

if __name__ == '__main__': process_faisalas()