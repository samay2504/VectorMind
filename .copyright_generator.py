#!/usr/bin/env python3
"""
Copyright Header Generator for VectorMind Project

═══════════════════════════════════════════════════════════════════════════
Copyright © 2025 Samay Mehar. All Rights Reserved.
PROPRIETARY SOFTWARE - PATENT PENDING
Author: Samay Mehar | Created: October 31 - November 1, 2025
VectorMind (Modality RAG System)
Unauthorized use is strictly prohibited and may result in legal action.
═══════════════════════════════════════════════════════════════════════════

This script generates and validates copyright headers across the codebase.
"""

COPYRIGHT_HEADER_FULL = '''"""
{description}

═══════════════════════════════════════════════════════════════════════════
Copyright © 2025 Samay Mehar. All Rights Reserved.

PROPRIETARY SOFTWARE - PATENT PENDING

Author: Samay Mehar
Created: October 31 - November 1, 2025
Project: VectorMind (Modality RAG System)

{additional_notes}

Unauthorized use is strictly prohibited and may result in legal action.
═══════════════════════════════════════════════════════════════════════════
"""
'''

COPYRIGHT_HEADER_SHORT = '''"""
{description}

═══════════════════════════════════════════════════════════════════════════
Copyright © 2025 Samay Mehar. All Rights Reserved.
PROPRIETARY SOFTWARE - PATENT PENDING
Author: Samay Mehar | Created: October 31 - November 1, 2025
Unauthorized use is strictly prohibited and may result in legal action.
═══════════════════════════════════════════════════════════════════════════
"""
'''

COPYRIGHT_COMMENT = '''#
# Copyright © 2025 Samay Mehar. All Rights Reserved.
# PROPRIETARY SOFTWARE - PATENT PENDING
# Author: Samay Mehar | Project: VectorMind (Modality RAG System)
# Unauthorized use is strictly prohibited and may result in legal action.
#
'''

def get_copyright_header(file_type: str, description: str, full: bool = False) -> str:
    """
    Generate appropriate copyright header based on file type.
    
    Args:
        file_type: File extension (py, js, md, etc.)
        description: Brief description of the file
        full: Whether to use full or short header
        
    Returns:
        Formatted copyright header string
    """
    if file_type in ['py', 'pyx', 'pyi']:
        if full:
            return COPYRIGHT_HEADER_FULL.format(
                description=description,
                additional_notes="This file implements core functionality created entirely from scratch."
            )
        else:
            return COPYRIGHT_HEADER_SHORT.format(description=description)
    
    elif file_type in ['yaml', 'yml', 'toml', 'ini', 'conf']:
        return COPYRIGHT_COMMENT
    
    elif file_type in ['js', 'ts', 'jsx', 'tsx', 'css', 'scss']:
        return f'''/*
 * Copyright © 2025 Samay Mehar. All Rights Reserved.
 * PROPRIETARY SOFTWARE - PATENT PENDING
 * Author: Samay Mehar | Project: VectorMind
 * Unauthorized use is strictly prohibited.
 */
'''
    
    elif file_type in ['html', 'xml']:
        return f'''<!--
  Copyright © 2025 Samay Mehar. All Rights Reserved.
  PROPRIETARY SOFTWARE - PATENT PENDING
  Author: Samay Mehar | Project: VectorMind
  Unauthorized use is strictly prohibited.
-->
'''
    
    elif file_type == 'md':
        return f'''<!--
═══════════════════════════════════════════════════════════════════════════
Copyright © 2025 Samay Mehar. All Rights Reserved.
PROPRIETARY SOFTWARE - PATENT PENDING
Author: Samay Mehar | Created: October 31 - November 1, 2025
VectorMind (Modality RAG System)
Unauthorized use is strictly prohibited and may result in legal action.
═══════════════════════════════════════════════════════════════════════════
-->

'''
    
    else:
        return COPYRIGHT_COMMENT

if __name__ == "__main__":
    print("Copyright Header Generator for VectorMind")
    print("=" * 70)
    print("\nThis tool generates copyright headers for all file types.")
    print("\nUsage:")
    print("  python .copyright_generator.py")
    print("\nAuthor: Samay Mehar")
    print("Project: VectorMind (Modality RAG System)")
    print("License: Proprietary - All Rights Reserved")
    print("=" * 70)
