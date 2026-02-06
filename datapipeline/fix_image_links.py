import re
import os
import glob

def fix_image_links(file_pattern):
    files = sorted(glob.glob(file_pattern))
    
    # Regex to capture the messy nested links. 
    # It seems they often span multiple lines or are just complex.
    # We look for something that contains "images/图X-Y.png" or "图 X-Y" inside a image tag structure.
    # A robust way is to find the Figure ID, then construct the clean link, 
    # and replace the whole determined block.
    
    # However, identifying the *block* to replace is tricky if it's messy.
    # Let's look at the structure:
    # ![
    # ![图 2-1](images/![图2-1](images/图2-1.png).png)
    # ](images/![图2-1](images/图2-1.png).png)
    
    # It seems to be valid markdown in a twisted way (image inside image).
    
    # Strategy:
    # 1. Read file.
    # 2. Find all occurrences of "图\s*(\d+-\d+)" that are inside some sort of markdown link/image structure 
    #    OR just find where the image SHOULD be.
    
    # Alternative Strategy:
    # The messy blocks seem to happen where a figure reference was intended.
    # Replaces any existing `![...](...)` that contains "图X-Y" or "图 X-Y" with the clean version.
    
    # Let's try to match the specific nested pattern first as it's the most destructive.
    # Pattern: `!\[\s*!\[.*?\]\(.*?\)\s*\]\(.*?\)` spanning lines.
    
    # But simpler: scan for ANY `images/.*图\s*(\d+-\d+).*\.png` and use it to assume there is a figure there.
    # The problem is the surrounding text.
    
    # Let's try to parse the file line by line, but buffering if we see `![`.
    
    # Improved Strategy:
    # The corruption seems to be specifically:
    # `![` newline `![text](url)` newline `](url)`
    # OR `![![text](url)](url)`
    
    # Regex for specific corruption:
    # `!\[\s*!\[图\s*(\d+-\d+)\]\(.*?\)\s*\]\(.*?\)`
    
    # Let's try a regex that matches the specific "triple-decker" or "double-decker" image nested tags.
    
    regex_nested = re.compile(r'!\[\s*!\[(图\s*\d+-\d+)\]\(.*?\)\s*\]\(.*?\)', re.DOTALL | re.MULTILINE)
    
    # Also handle the case where it might be `![图 2-1](images/![...].png)` (link inside url)
    regex_link_in_url = re.compile(r'!\[(.*?)\]\((images/!\[.*?\]\(.*?\)\.png)\)', re.DOTALL)

    for filepath in files:
        if "chapter-01" in filepath:
            continue # Skip chapter 1 as it is the reference
            
        print(f"Processing {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Function to replace matched bad link with clean link
        def replace_match(match):
            # Try to extract "图 X-Y" or "图X-Y" from the whole match string
            whole_str = match.group(0)
            id_match = re.search(r'图\s*(\d+-\d+)', whole_str)
            if id_match:
                fig_id = id_match.group(1) # e.g. "2-1"
                # Check if file exists (optional, but good for validation)
                # filename = f"图{fig_id}.png"
                clean_link = f"![图 {fig_id}](images/图{fig_id}.png)"
                return clean_link
            return whole_str # Return original if we can't find ID
            
        # 1. Fix the multi-line nested structure
        # Matches: ![ \n ![图 2-1](...) \n ](...)
        content = regex_nested.sub(replace_match, content)
        
        # 2. Fix other potential weirdness
        # e.g. `![图 3-1](images/![图3-1](images/图3-1.png).png)`
        # A simpler regex to find any Markdown image link that looks "suspiciously long" or contains `![` inside the URL part?
        # Or just find any link that refers to a figure and normalize it.
        
        # Broad Re-normalization Strategy:
        # Find any `![ALT](URL)` where ALT or URL contains "图X-Y"
        # And replace it with `![图 X-Y](images/图X-Y.png)`
        # This is powerful but risky if it targets normal text. 
        # But `![` `)` boundaries should keep it safe.
        
        pattern_broad = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
        
        def normalize_figure_link(match):
            alt = match.group(1)
            url = match.group(2)
            
            # Reset if it's already clean? 
            # Clean: `![图 2-1](images/图2-1.png)`
            # ALT="图 2-1", URL="images/图2-1.png"
            
            # Check if this is a figure link
            combined = alt + url
            id_match = re.search(r'图\s*(\d+-\d+)', combined)
            
            if id_match:
                fig_id = id_match.group(1)
                expected_filename = f"图{fig_id}.png"
                
                # Check if it is already correct
                if url.strip() == f"images/{expected_filename}" and (alt.strip() == f"图 {fig_id}" or alt.strip() == f"图{fig_id}"):
                    return match.group(0) # No change
                
                # If it looks broken (contains nested ![ or just wrong path), fix it
                # Logic: If it's capturing a figure, standardise it.
                # However, user might have custom Alt text like "数字化转型 (图 1-3)". We should preserve Alt text if it's not "messy".
                # Messy Alt text usually contains `![` or newlines.
                
                new_alt = alt
                if "![" in alt or "\n" in alt:
                    new_alt = f"图 {fig_id}"
                
                # Force the correct path
                new_link = f"![{new_alt}](images/{expected_filename})"
                return new_link
            
            return match.group(0) # Not a figure link
            
        content = pattern_broad.sub(normalize_figure_link, content)
        
        
        # 3. Clean up duplicates
        # Sometimes we have:
        # ![图 3-1](...)
        # ![图 3-1](...)
        # We can remove consecutive identical lines, or identical links.
        
        # 4. cleanup trailing garbage left by previous incomplete regex
        # e.g. ![图 2-1](images/图2-1.png).png)
        regex_trailing_garbage = re.compile(r'(!\[.*?\]\(images/.*?\))\.png\)')
        content = regex_trailing_garbage.sub(r'\1', content)

        lines = content.split('\n')
        new_lines = []
        last_line = None
        
        # Regex to identify debris lines
        regex_debris = re.compile(r'^(\.png\)|\]\(images/|\]\(images/!\[.*?\)\.png\))$')

        for line in lines:
            stripped = line.strip()
            # Skip known garbage lines
            if regex_debris.match(stripped):
                continue
            # Skip empty lines if they are between figures (optional, but might be nice)
            
            # Deduplication
            if stripped == last_line and "![" in line and "图" in line:
                continue # Skip duplicate figure line
                
            new_lines.append(line)
            # Update last_line only if it wasn't skipped (so we catch duplicates separated by skipped garbage)
            last_line = stripped
            
        content = '\n'.join(new_lines)

        if content != original_content:
            print(f"Fixed {filepath}")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            print(f"No changes for {filepath}")

if __name__ == "__main__":
    base_dir = "/Users/david/david_project/智能体/数据治理/参考文档/数据之道"
    # Target chapters 02-10
    fix_image_links(os.path.join(base_dir, "chapter-*-detailed.md"))
