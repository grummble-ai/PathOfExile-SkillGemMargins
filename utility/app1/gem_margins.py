"""
Path of Exile Skill Gem Margin Calculator

This module calculates profit margins for skill gems in Path of Exile by analyzing
the cost of leveling/qualitying gems versus their market value. It handles different
gem types (regular, awakened, exceptional, special) and calculates risk-adjusted returns.

Author: PoE Academy
"""

import os
import warnings
import pandas as pd
from utility.app1 import skillgems_data_handler as dh
from os import path
from typing import Dict, List, Tuple

# Suppress pandas chained assignment warnings
pd.options.mode.chained_assignment = None

# =============================================================================
# CONSTANTS
# =============================================================================

# Experience requirements for different gem types (to max level)
GEM_EXPERIENCE = {
    "awakened": 1920762677,      # to level 5
    "exceptional": 1666045137,   # to level 3 (Enhance, Empower, Enlighten)
    "bloodandsand": 529166003,   # to level 6
    "brandrecall": 341913067,    # to level 6
    "regular": 684009294,        # to level 20/20
}

# Calculate maximum experience for normalization
MAX_EXP = max(GEM_EXPERIENCE.values())

# Create normalized experience dictionary
GEM_EXPERIENCE_NORM = {
    f"{gem_type}_norm": exp / MAX_EXP 
    for gem_type, exp in GEM_EXPERIENCE.items()
}

# Combine both dictionaries
GEM_EXPERIENCE = {**GEM_EXPERIENCE, **GEM_EXPERIENCE_NORM}

# =============================================================================
# DATA LOADING FUNCTIONS
# =============================================================================

def load_gem_info() -> pd.DataFrame:
    """
    Load gem information from Excel files with fallback options.
    
    Returns:
        pd.DataFrame: DataFrame containing gem information (name, color, type, base_gem, discriminator)
    """
    files_to_try = [
        "gem_colors_325.xlsx", 
        "gem_colors_324.xlsx", 
        "gem_colors_323.xlsx", 
        "gem_colors.xlsx"
    ]
    
    for filename in files_to_try:
        try:
            file_path = path.join(os.getcwd(), "utility", "app1", filename)
            return pd.read_excel(file_path)
        except (PermissionError, FileNotFoundError):
            continue
    
    # Fallback: create minimal dataframe to avoid errors
    print("Warning: Could not load gem colors file, using minimal data")
    return pd.DataFrame({
        'name': [], 'color': [], 'type': [], 'base_gem': [], 'discriminator': []
    })

def load_regular_gem_xp() -> pd.DataFrame:
    """
    Load regular gem experience requirements from pickle file.
    
    Returns:
        pd.DataFrame: Experience requirements matrix for regular gems
    """
    file_path = path.join(os.getcwd(), "utility", "app1", "regular_gem_xp_df")
    return pd.read_pickle(file_path)

# =============================================================================
# GEM CLASSIFICATION FUNCTIONS
# =============================================================================

def classify_gem_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify gems into types based on their names and characteristics.
    
    Args:
        df: DataFrame containing gem data with 'name' column
        
    Returns:
        pd.DataFrame: DataFrame with added 'gem_type' column
    """
    df = df.copy()
    
    # Load gem info and create mapping
    gem_info = load_gem_info()
    type_mapping = dict(gem_info[['name', 'type']].values)
    
    # Apply initial mapping
    df['gem_type'] = df['name'].map(type_mapping)
    
    # Standardize skill and support gems as regular
    df.loc[df['gem_type'].isin(['skill', 'support']), 'gem_type'] = 'regular'
    
    # Classify special gem types
    gem_classifications = {
        'awakened': df['name'].str.contains('Awakened'),
        'exceptional': df['name'].str.contains('Enlighten|Empower|Enhance'),
        'special': df['name'].isin(['Blood and Sand', 'Brand Recall'])
    }
    
    for gem_type, condition in gem_classifications.items():
        df.loc[condition, 'gem_type'] = gem_type
    
    return df

def add_gem_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add gem color, base gem, and discriminator information.
    
    Args:
        df: DataFrame containing gem data
        
    Returns:
        pd.DataFrame: DataFrame with added gem metadata columns
    """
    df = df.copy()
    gem_info = load_gem_info()
    
    # Create mappings for efficient lookup
    color_mapping = dict(zip(gem_info['name'], gem_info['color']))
    base_gem_mapping = dict(zip(gem_info['name'], gem_info['base_gem']))
    discriminator_mapping = dict(zip(gem_info['name'], gem_info['discriminator']))
    
    # Apply mappings
    df['gem_color'] = df['skill'].map(color_mapping)
    df['base_gem'] = df['skill'].map(base_gem_mapping)
    df['discriminator'] = df['skill'].map(discriminator_mapping)
    
    # Check for missing gems and warn
    missing_gems = df[df['gem_color'].isna()]['name'].dropna().unique()
    if len(missing_gems) > 0:
        warnings.warn(
            f"Missing gem color tags for: {missing_gems}",
            UserWarning
        )
    
    return df

# =============================================================================
# ECONOMIC CALCULATION FUNCTIONS
# =============================================================================

def find_base_gem(df_gem_group: pd.DataFrame) -> pd.Series:
    """
    Find the cheapest base gem in a group of gems with the same name.
    
    Args:
        df_gem_group: DataFrame containing gems with the same name
        
    Returns:
        pd.Series: Row representing the cheapest base gem
    """
    # Find the cheapest entry by combining all criteria at once
    min_corrupted = df_gem_group['corrupted'].min()
    min_quality = df_gem_group['gemQuality'].min()
    min_level = df_gem_group['gemLevel'].min()
    
    # Filter by all criteria simultaneously
    filtered = df_gem_group[
        (df_gem_group['corrupted'] == min_corrupted) &
        (df_gem_group['gemQuality'] == min_quality) &
        (df_gem_group['gemLevel'] == min_level)
    ]
    
    # Get the one with minimum chaos value
    min_chaos_idx = filtered['value_chaos'].idxmin()
    return filtered.loc[min_chaos_idx]

def calculate_chaos_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate chaos orb values for all gem upgrade paths.
    
    Args:
        df: DataFrame containing gem data
        
    Returns:
        pd.DataFrame: DataFrame with calculated chaos values
    """
    results = []
    
    for gem_name in df['name'].unique():
        gem_group = df[df['name'] == gem_name]
        base_gem = find_base_gem(gem_group)
        
        for _, gem in gem_group.iterrows():
            # Calculate economic values
            buy_chaos = base_gem['value_chaos']
            sell_chaos = gem['value_chaos']
            margin_chaos = sell_chaos - buy_chaos
            roi = margin_chaos / buy_chaos if buy_chaos > 0 else 0
            
            # Create upgrade path string
            base_str = f"[{base_gem['gemLevel']}/{base_gem['gemQuality']}]"
            target_str = f"[{gem['gemLevel']}/{gem['gemQuality']}]"
            corruption_mark = " ©" if gem['corrupted'] else ""
            upgrade_path = f"{base_str} -> {target_str}{corruption_mark}"
            
            # Add calculated values
            gem_result = gem.copy()
            gem_result.update({
                'buy_c': buy_chaos,
                'sell_c': sell_chaos,
                'margin_c': margin_chaos,
                'roi': roi,
                'gem_level_base': base_gem['gemLevel'],
                'gem_quality_base': base_gem['gemQuality'],
                'upgrade_path': upgrade_path
            })
            
            results.append(gem_result)
    
    return pd.DataFrame(results)

def calculate_divine_values(df: pd.DataFrame, chaos_to_divine: float) -> pd.DataFrame:
    """
    Convert chaos values to divine orb values.
    
    Args:
        df: DataFrame with chaos values
        chaos_to_divine: Conversion rate from chaos to divine orbs
        
    Returns:
        pd.DataFrame: DataFrame with divine orb values added
    """
    df = df.copy()
    df['buy_divine'] = df['buy_c'] / chaos_to_divine
    df['sell_divine'] = df['sell_c'] / chaos_to_divine
    df['margin_divine'] = df['margin_c'] / chaos_to_divine
    return df

def calculate_regular_gem_xp_margins(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate XP-normalized margins for regular gems.
    
    Args:
        df: DataFrame containing gem data
        
    Returns:
        pd.DataFrame: DataFrame with XP-normalized margins
    """
    df = df.copy()
    xp_matrix = load_regular_gem_xp()
    
    for idx, row in df.iterrows():
        if row['gem_type'] not in ['regular', 'transfigured']:
            continue
            
        # Skip if no upgrade (same level/quality)
        if (row['gem_level_base'] == row['gemLevel'] and 
            row['gem_quality_base'] == row['gemQuality']):
            df.loc[idx, 'margin_gem_specific'] = row['margin_divine']
            continue
        
        # Calculate XP indices
        base_quality_offset = 20 if row['gem_quality_base'] > 0 else 0
        target_quality_offset = 20 if row['gemQuality'] > 0 else 0
        
        x_idx = row['gem_level_base'] - 1 + base_quality_offset
        
        if row['gemQuality'] > 0 and 1 <= row['gemLevel'] <= 20:
            y_idx = row['gemLevel'] - 1 + target_quality_offset
        elif row['gemQuality'] > 0 and row['gemLevel'] == 21:
            y_idx = row['gemLevel'] - 2 + target_quality_offset
        else:
            y_idx = row['gemLevel'] - 1
        
        # Get XP requirement and calculate normalized margin
        xp_required = xp_matrix.iloc[y_idx, x_idx]
        margin_normalized = row['margin_divine'] / (xp_required / MAX_EXP)
        df.loc[idx, 'margin_gem_specific'] = margin_normalized
    
    return df

def calculate_margins_and_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate XP-normalized margins and risk-adjusted returns for all gem types.
    
    Args:
        df: DataFrame containing gem data
        
    Returns:
        pd.DataFrame: DataFrame with margins, rankings, and risk adjustments
    """
    df = df.copy()
    
    # Calculate XP-normalized margins for special gem types
    special_gem_mappings = {
        'Awakened': 'awakened_norm',
        'Enlighten|Empower|Enhance': 'exceptional_norm',
        'Blood and Sand': 'bloodandsand_norm',
        'Brand Recall': 'brandrecall_norm'
    }
    
    for pattern, exp_key in special_gem_mappings.items():
        mask = df['name'].str.contains(pattern, regex=True)
        df.loc[mask, 'margin_gem_specific'] = (
            df.loc[mask, 'margin_divine'] / GEM_EXPERIENCE[exp_key]
        )
    
    # Calculate margins for regular gems
    df = calculate_regular_gem_xp_margins(df)
    
    # Ensure margin_gem_specific is numeric
    df['margin_gem_specific'] = pd.to_numeric(df['margin_gem_specific'], errors='coerce')
    
    # Calculate risk-adjusted returns
    # Corrupted gems have 1/8 chance of success (12.5% success rate)
    df['risk_adjusted_return'] = df['margin_divine'].copy()
    corrupted_mask = df['corrupted'] == True
    df.loc[corrupted_mask, 'risk_adjusted_return'] = (
        df.loc[corrupted_mask, 'sell_divine'] * 0.125 - 
        df.loc[corrupted_mask, 'buy_divine']
    )
    
    # Calculate risk-adjusted ROI
    df['risk_adjusted_roi'] = df['risk_adjusted_return'] / df['buy_divine']
    
    # Calculate rankings
    df['ranking_from_margin_gem_specific'] = df['margin_gem_specific'].rank(ascending=False)
    df['ranking_from_roi'] = df['roi'].rank(ascending=False)
    
    # Filter out non-profitable entries
    df = df[df['roi'] > 0]
    
    return df

def filter_low_confidence(df: pd.DataFrame, min_listings: int) -> pd.DataFrame:
    """
    Remove gems with too few market listings for reliable pricing.
    
    Args:
        df: DataFrame containing gem data
        min_listings: Minimum number of listings required
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    gem_listing_counts = df.groupby('name')['listingcount'].first()
    reliable_gems = gem_listing_counts[gem_listing_counts > min_listings].index
    return df[df['name'].isin(reliable_gems)]

# =============================================================================
# TRADE URL GENERATION FUNCTIONS
# =============================================================================

def create_trade_url(league: str, base_gem: str, discriminator: str) -> str:
    """
    Create a Path of Exile trade search URL for a specific gem.
    
    Args:
        league: Current league name
        base_gem: Base gem name
        discriminator: Gem discriminator (alt_x, alt_y, etc.)
        
    Returns:
        str: Trade search URL
    """
    # Ensure base_gem is a string and handle missing values
    if not isinstance(base_gem, str) or pd.isna(base_gem):
        base_gem = "UnknownGem"
    name_str = f'%22{base_gem.replace(" ", "%20")}%22'
    
    discriminator_str = ""
    if isinstance(discriminator, str) and discriminator in ['alt_x', 'alt_y']:
        discriminator_str = f',%22discriminator%22:%22{discriminator}%22'
    
    url_template = (
        f"https://www.pathofexile.com/trade/search/{league}?q="
        "{%22query%22:{%22type%22:{%22option%22:" + name_str + discriminator_str + "},"
        "%22stats%22:[{%22type%22:%22and%22,%22filters%22:[],%22disabled%22:false}],"
        "%22status%22:{%22option%22:%22online%22},"
        "%22filters%22:{%22misc_filters%22:{%22filters%22:{%22corrupted%22:{%22option%22:%22false%22}},"
        "%22disabled%22:false}}}}"
    )
    
    return url_template

def create_trade_button_html(url: str) -> str:
    """
    Create HTML for a trade button.
    
    Args:
        url: Trade search URL
        
    Returns:
        str: HTML button code
    """
    return (
        f'<a class="button" target="_blank" title="Buy on pathofexile.com/trade" '
        f'href={url} role="button" data-variant="round" data-size="small" '
        f'style="font-family: "Source Sans Pro", sans-serif; color: rgb(255, 75, 75);">'
        f'Trade <svg aria-hidden="true" data-prefix="fas" data-icon="exchange-alt" '
        f'class="icon-exchange-alt-solid_svg__svg-inline--fa icon-exchange-alt-solid_svg__fa-exchange-alt '
        f'icon-exchange-alt-solid_svg__fa-w-16" viewBox="0 0 512 512" width="1em" height="1em">'
        f'<path fill="currentColor" d="M0 168v-16c0-13.255 10.745-24 24-24h360V80c0-21.367 25.899-32.042 '
        f'40.971-16.971l80 80c9.372 9.373 9.372 24.569 0 33.941l-80 80C409.956 271.982 384 261.456 '
        f'384 240v-48H24c-13.255 0-24-10.745-24-24zm488 152H128v-48c0-21.314-25.862-32.08-40.971-16.971l-80 80c-9.372 '
        f'9.373-9.372 24.569 0 33.941l80 80C102.057 463.997 128 453.437 128 432v-48h360c13.255 0 24-10.745 24-24v-16c0-13.255-10.745-24-24-24z"></path></svg></a>'
    )

def add_trade_urls(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add trade URLs and HTML buttons to the DataFrame.
    
    Args:
        df: DataFrame containing gem data
        
    Returns:
        pd.DataFrame: DataFrame with trade URLs and HTML buttons
    """
    df = df.copy()
    league = dh.load_league()
    
    df['query_url'] = df.apply(
        lambda row: create_trade_url(league, row['base_gem'], row['discriminator']), 
        axis=1
    )
    
    df['query_html'] = df['query_url'].apply(create_trade_button_html)
    
    return df

# =============================================================================
# MAIN PROCESSING FUNCTION
# =============================================================================

def create_json_data() -> None:
    """
    Main function to process gem data and create JSON output.
    
    This function:
    1. Loads raw currency and gem data
    2. Calculates economic values and margins
    3. Adds gem metadata and trade URLs
    4. Saves the processed data as JSON
    """
    # Load raw data
    currency_data = pd.DataFrame.from_dict(
        dh.load_raw_dict(type="Currency"), 
        orient="index"
    )
    gem_data = pd.DataFrame.from_dict(
        dh.load_raw_dict(type="Gems"), 
        orient="index"
    )
    
    # Get currency conversion rates
    chaos_to_divine = currency_data[
        currency_data['name'] == "Divine Orb"
    ]['value_chaos'].iloc[0]
    
    # Initialize DataFrame with required columns
    df = gem_data.sort_values(['skill', 'qualityType', 'gemLevel'], ascending=[True, True, False])
    
    # Remove Vaal skill gems
    df = df[~df['name'].str.contains("Vaal")]
    
    # Initialize new columns
    new_columns = [
        'gem_type', 'gem_level_base', 'gem_quality_base', 'upgrade_path',
        'buy_c', 'sell_c', 'margin_c', 'buy_divine', 'sell_divine', 'margin_divine',
        'margin_gem_specific', 'roi', 'ranking_from_roi', 'gem_color', 'base_gem',
        'discriminator', 'query_url', 'query_html'
    ]
    
    for col in new_columns:
        df[col] = ""
    
    # Process the data
    df = classify_gem_types(df)
    df = calculate_chaos_values(df)
    df = calculate_divine_values(df, chaos_to_divine)
    df = calculate_margins_and_rankings(df)
    df = add_gem_metadata(df)
    df = add_trade_urls(df)
    
    # Save to JSON
    gems_analyzed = df.to_dict(orient="index")
    dh.save_json(gems_analyzed)
