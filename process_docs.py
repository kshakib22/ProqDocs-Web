import os
import re

files_to_process = [
    "src/content/docs/entities/Boq Model.md",
    "src/content/docs/entities/BoqEntryController.md",
    "src/content/docs/entities/BoqEntryModel.md",
    "src/content/docs/entities/BoqEntryResource.md",
    "src/content/docs/entities/BoqSheet Model.md",
    "src/content/docs/entities/BoqSheet-Model.md",
    "src/content/docs/entities/BoqSheetController.md",
    "src/content/docs/entities/BoqSheetEntryService.md",
    "src/content/docs/entities/BoqSheetMergeModel.md",
    "src/content/docs/entities/BoqSheetMergeResource.md",
    "src/content/docs/entities/BoqSheetMergeService.md",
    "src/content/docs/entities/BoqSheetModel.md",
    "src/content/docs/entities/BoqSheetResource.md",
    "src/content/docs/entities/BoqSheetService.md",
    "src/content/docs/entities/Delivery-Domain.md",
    "src/content/docs/entities/Elasticsearch-Domain.md",
    "src/content/docs/entities/Project-Domain.md",
    "src/content/docs/entities/PurchaseList-Domain.md",
    "src/content/docs/entities/PurchaseOrder-Domain.md",
    "src/content/docs/entities/Quotation Model.md",
    "src/content/docs/entities/Quotation-Model.md",
    "src/content/docs/entities/QuotationController.md",
    "src/content/docs/entities/QuotationResource.md",
    "src/content/docs/entities/QuotationService.md",
    "src/content/docs/entities/QuotationsServiceResource.md",
    "src/content/docs/entities/QutationService Model.md",
    "src/content/docs/entities/QutationService-Model.md",
    "src/content/docs/entities/QutationServiceModel.md",
    "src/content/docs/entities/Rfq Model.md",
    "src/content/docs/entities/Rfq-Model.md",
    "src/content/docs/entities/RfqController.md",
    "src/content/docs/entities/RfqModel.md",
    "src/content/docs/entities/RfqResource.md",
    "src/content/docs/entities/RfqService.md",
    "src/content/docs/entities/Vendor-Domain.md"
]

all_files = [
    "src/content/docs/01-Projects/Tech-Debt-Ledger.md",
    "src/content/docs/log.md",
    "src/content/docs/index.md",
    "src/content/docs/entities/RfqModel.md",
    "src/content/docs/entities/QutationServiceModel.md",
    "src/content/docs/entities/QuotationsServiceResource.md",
    "src/content/docs/entities/Product-Domain.md",
    "src/content/docs/entities/BoqEntryController.md",
    "src/content/docs/entities/RfqController.md",
    "src/content/docs/entities/Payment-Domain.md",
    "src/content/docs/entities/Quotation Model.md",
    "src/content/docs/entities/Rfq-Model.md",
    "src/content/docs/entities/PurchaseList-Domain.md",
    "src/content/docs/entities/RfqResource.md",
    "src/content/docs/entities/Elasticsearch-Domain.md",
    "src/content/docs/entities/QuotationService.md",
    "src/content/docs/entities/BoqSheet-Model.md",
    "src/content/docs/entities/BoqSheetEntryService.md",
    "src/content/docs/entities/QuotationResource.md",
    "src/content/docs/entities/QutationService Model.md",
    "src/content/docs/entities/PurchaseOrder-Domain.md",
    "src/content/docs/entities/BoqSheetMergeResource.md",
    "src/content/docs/entities/BoqEntryModel.md",
    "src/content/docs/entities/Rfq Model.md",
    "src/content/docs/entities/RFQ-Quotation-Domain.md",
    "src/content/docs/entities/BoqSheetMergeService.md",
    "src/content/docs/entities/QuotationController.md",
    "src/content/docs/entities/QutationService-Model.md",
    "src/content/docs/entities/Vendor-Domain.md",
    "src/content/docs/entities/BoqSheetService.md",
    "src/content/docs/entities/BoqSheetResource.md",
    "src/content/docs/entities/BoqSheet Model.md",
    "src/content/docs/entities/BoqSheetModel.md",
    "src/content/docs/entities/BoqEntry-BoqSheet-Domain.md",
    "src/content/docs/entities/BoqSheetMergeModel.md",
    "src/content/docs/entities/RfqService.md",
    "src/content/docs/entities/Boq Model.md",
    "src/content/docs/entities/Quotation-Model.md",
    "src/content/docs/entities/Delivery-Domain.md",
    "src/content/docs/entities/BoqSheetController.md",
    "src/content/docs/entities/BoqEntryResource.md",
    "src/content/docs/entities/Project-Domain.md"
]

file_map = {}
for f in all_files:
    rel_path = f.replace("src/content/docs/", "")
    name = os.path.basename(rel_path)
    name_no_ext = os.path.splitext(name)[0]
    file_map[name] = rel_path
    file_map[name_no_ext] = rel_path
    # Also add versions without hyphens/spaces for fuzzy matching
    fuzzy_name = name.replace("-", "").replace(" ", "").lower()
    file_map[fuzzy_name] = rel_path
    fuzzy_name_no_ext = name_no_ext.replace("-", "").replace(" ", "").lower()
    file_map[fuzzy_name_no_ext] = rel_path

def resolve_link(current_file_rel, target):
    target_clean = target.split("#")[0].strip()
    anchor = "#" + target.split("#")[1] if "#" in target else ""
    
    found_rel_path = None
    if target_clean in file_map:
        found_rel_path = file_map[target_clean]
    elif (target_clean + ".md") in file_map:
        found_rel_path = file_map[target_clean + ".md"]
    else:
        # Try fuzzy match
        fuzzy_target = target_clean.replace("-", "").replace(" ", "").lower()
        if fuzzy_target in file_map:
            found_rel_path = file_map[fuzzy_target]
    
    if found_rel_path:
        current_dir = os.path.dirname(current_file_rel)
        rel_to_target = os.path.relpath(found_rel_path, current_dir)
        if not rel_to_target.startswith("."):
            rel_to_target = "./" + rel_to_target
        return rel_to_target + anchor
    return None

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    current_file_rel = file_path.replace("src/content/docs/", "")
    
    # 1. Frontmatter
    if not content.startswith("---"):
        title = os.path.basename(file_path).replace(".md", "").replace("-", " ").title()
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
        content = f"---\ntitle: \"{title}\"\n---\n\n" + content
    else:
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            if "title:" not in fm_text:
                title = os.path.basename(file_path).replace(".md", "").replace("-", " ").title()
                h1_match = re.search(r"^#\s+(.+)$", parts[2], re.MULTILINE)
                if h1_match:
                    title = h1_match.group(1).strip()
                new_fm = fm_text.rstrip() + f"\ntitle: \"{title}\"\n"
                content = "---\n" + new_fm + "---" + parts[2]

    # 2. Wiki links [[Target]] or [[Target|Text]]
    def replace_wiki(match):
        target = match.group(1)
        text = target
        if "|" in target:
            target, text = target.split("|", 1)
        
        resolved = resolve_link(current_file_rel, target)
        if resolved:
            return f"[{text}]({resolved})"
        else:
            # Rule 1: Replace ALL wiki links [[Target]] with [Target](./Target.md)
            # Rule 4: preserve exact filename
            if not "/" in target:
                return f"[{text}](./{target}.md)"
            return match.group(0)

    content = re.sub(r"\[\[([^\]]+)\]\]", replace_wiki, content)

    # 3. Standard links [Text](Target)
    def replace_std(match):
        text = match.group(1)
        target = match.group(2)
        
        if target.startswith("http") or target.startswith("#") or target.startswith("/") or target.startswith("."):
            return match.group(0)
        
        resolved = resolve_link(current_file_rel, target)
        if resolved:
            return f"[{text}]({resolved})"
        else:
            # Rule 2: Ensure internal markdown link [Text](Target) becomes [Text](./Target.md) if in same folder
            if not "/" in target:
                if not target.endswith(".md"):
                    return f"[{text}](./{target}.md)"
                else:
                    return f"[{text}](./{target})"
            return match.group(0)

    content = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_std, content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

for f in files_to_process:
    if os.path.exists(f):
        process_file(f)
