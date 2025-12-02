#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飲食店売上データ集計スクリプト

処理内容:
1. 複数のCSVファイルを統合
2. キャンセル済みオーダーを除外
3. 売上が立っていない行（価格が0以下）を除外
4. 商品IDと商品名を分離
5. 月別の売上個数と売上高を集計
"""

import pandas as pd
import glob
import os
from datetime import datetime
import sys


def load_and_merge_csv_files(folder_path):
    """
    指定フォルダ内のすべてのCSVファイルを読み込んで統合
    
    Args:
        folder_path (str): CSVファイルが格納されているフォルダパス
        
    Returns:
        pd.DataFrame: 統合されたデータフレーム
    """
    # 元の売上データCSVのみを対象（集計結果ファイルは除外）
    all_csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    csv_files = [f for f in all_csv_files if not os.path.basename(f).startswith('売上集計結果')]
    
    if not csv_files:
        print(f"エラー: {folder_path} にCSVファイルが見つかりません")
        sys.exit(1)
    
    print(f"\n{len(csv_files)}個のCSVファイルを読み込んでいます...")
    for csv_file in csv_files:
        print(f"  - {os.path.basename(csv_file)}")
    
    # すべてのCSVを読み込んで統合
    dfs = []
    expected_columns = ['D.オーダーステータス', 'D.数量', 'D.価格', 'D.商品', 
                       'D.商品カテゴリ1', 'D.商品カテゴリ2', 'H.集計対象営業年月日']
    
    for csv_file in csv_files:
        try:
            # まずファイルを読んで正しいヘッダー行を探す
            with open(csv_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # ヘッダー行を探す
            header_row = None
            for i, line in enumerate(lines):
                if 'D.オーダーステータス' in line:
                    header_row = i
                    break
            
            if header_row is None:
                print(f"警告: {os.path.basename(csv_file)} にヘッダー行が見つかりません")
                continue
            
            # ヘッダー行からデータを読み込む
            df = pd.read_csv(csv_file, encoding='utf-8', skiprows=header_row)
            
        except UnicodeDecodeError:
            # UTF-8で読めない場合はShift-JISで試す
            try:
                with open(csv_file, 'r', encoding='shift-jis') as f:
                    lines = f.readlines()
                
                header_row = None
                for i, line in enumerate(lines):
                    if 'D.オーダーステータス' in line:
                        header_row = i
                        break
                
                if header_row is None:
                    print(f"警告: {os.path.basename(csv_file)} にヘッダー行が見つかりません")
                    continue
                
                df = pd.read_csv(csv_file, encoding='shift-jis', skiprows=header_row)
            except Exception as e:
                print(f"エラー: {os.path.basename(csv_file)} の読み込みに失敗: {e}")
                continue
        except Exception as e:
            print(f"エラー: {os.path.basename(csv_file)} の読み込みに失敗: {e}")
            continue
        
        # データが正しく読み込めているか確認
        if df is not None and len(df) > 0:
            # 列名が正しいか確認
            if all(col in df.columns for col in expected_columns):
                dfs.append(df)
                print(f"  ✓ {os.path.basename(csv_file)}: {len(df):,}行")
            else:
                print(f"警告: {os.path.basename(csv_file)} の列名が不正です: {df.columns.tolist()}")
        else:
            print(f"警告: {os.path.basename(csv_file)} にデータがありません")
    
    merged_df = pd.concat(dfs, ignore_index=True)
    print(f"統合完了: {len(merged_df):,}行のデータを読み込みました")
    
    return merged_df


def clean_data(df):
    """
    データのクリーニング処理
    
    Args:
        df (pd.DataFrame): 元のデータフレーム
        
    Returns:
        pd.DataFrame: クリーニング後のデータフレーム
    """
    print("\nデータクリーニング中...")
    
    # 元の行数
    original_rows = len(df)
    
    # 1. キャンセル済みオーダーを除外
    df = df[~df['D.オーダーステータス'].str.contains('キャンセル', na=False)].copy()
    print(f"  - キャンセル済みを除外: {original_rows:,} → {len(df):,}行")
    
    # 2. 価格を数値型に変換
    df['D.価格'] = pd.to_numeric(df['D.価格'], errors='coerce')
    df['D.数量'] = pd.to_numeric(df['D.数量'], errors='coerce')
    
    # 3. 売上が0以下の行を除外（返品や無効なデータ）
    before_price_filter = len(df)
    df = df[df['D.価格'] > 0]
    print(f"  - 価格が0以下を除外: {before_price_filter:,} → {len(df):,}行")
    
    # 4. 数量が0以下の行を除外
    before_qty_filter = len(df)
    df = df[df['D.数量'] > 0]
    print(f"  - 数量が0以下を除外: {before_qty_filter:,} → {len(df):,}行")
    
    # 5. 商品IDと商品名を分離
    print("  - 商品IDと商品名を分離中...")
    df[['商品ID', '商品名']] = df['D.商品'].str.split(':', n=1, expand=True)
    
    # 6. 日付を datetime型に変換
    df['H.集計対象営業年月日'] = pd.to_datetime(df['H.集計対象営業年月日'])
    
    # 7. 年月列を追加
    df['年月'] = df['H.集計対象営業年月日'].dt.to_period('M')
    
    print(f"クリーニング完了: 最終的に{len(df):,}行のデータが有効です\n")
    
    return df


def aggregate_sales(df):
    """
    商品ごと・月別の売上を集計
    
    Args:
        df (pd.DataFrame): クリーニング済みデータフレーム
        
    Returns:
        pd.DataFrame: 集計結果のデータフレーム
    """
    print("売上集計中...")
    
    # 売上高を計算（価格 × 数量）
    df['売上高'] = df['D.価格'] * df['D.数量']
    
    # 商品ごとの基本情報を取得
    product_info = df.groupby('商品ID').first()[
        ['商品名', 'D.商品カテゴリ1', 'D.商品カテゴリ2', 'D.価格']
    ].reset_index()
    product_info.columns = ['商品ID', '商品名', '商品カテゴリ①', '商品カテゴリ②', '商品単価']
    
    # 月別の売上個数を集計
    qty_pivot = df.pivot_table(
        index='商品ID',
        columns='年月',
        values='D.数量',
        aggfunc='sum',
        fill_value=0
    )
    
    # 月別の売上高を集計
    sales_pivot = df.pivot_table(
        index='商品ID',
        columns='年月',
        values='売上高',
        aggfunc='sum',
        fill_value=0
    )
    
    # 列名を整形（売上個数）
    qty_pivot.columns = [f'{col}売上個数' for col in qty_pivot.columns]
    
    # 列名を整形（売上高）
    sales_pivot.columns = [f'{col}売上高' for col in sales_pivot.columns]
    
    # すべてを結合
    result = product_info.merge(qty_pivot, on='商品ID', how='left')
    result = result.merge(sales_pivot, on='商品ID', how='left')
    
    # 累計売上個数を計算
    qty_columns = [col for col in result.columns if '売上個数' in col and col != '累計売上個数']
    result['累計売上個数'] = result[qty_columns].sum(axis=1)
    
    # 累計売上を計算
    sales_columns = [col for col in result.columns if '売上高' in col and col != '累計売上']
    result['累計売上'] = result[sales_columns].sum(axis=1)
    
    # 列の順序を整理
    base_columns = ['商品カテゴリ①', '商品カテゴリ②', '商品名', '商品ID', '商品単価', '累計売上個数', '累計売上']
    
    # 月別列をソート
    month_columns = sorted([col for col in result.columns if col not in base_columns])
    
    # 売上個数と売上高を分離してソート
    qty_cols = sorted([col for col in month_columns if '売上個数' in col])
    sales_cols = sorted([col for col in month_columns if '売上高' in col])
    
    # 最終的な列順序
    final_columns = base_columns + qty_cols + sales_cols
    result = result[final_columns]
    
    # 累計売上でソート（降順）
    result = result.sort_values('累計売上', ascending=False)
    
    print(f"集計完了: {len(result)}商品の売上データを生成しました")
    print(f"集計期間: {qty_cols[0].replace('売上個数', '')} ～ {qty_cols[-1].replace('売上個数', '')}")
    
    return result


def main():
    """
    メイン処理
    """
    print("=" * 60)
    print("飲食店売上データ集計スクリプト")
    print("=" * 60)
    
    # スクリプトと同じフォルダのCSVファイルを処理
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. CSVファイルを読み込んで統合
    df = load_and_merge_csv_files(script_dir)
    
    # 2. データクリーニング
    df_cleaned = clean_data(df)
    
    # 3. 売上集計
    result = aggregate_sales(df_cleaned)
    
    # 4. 結果を保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(script_dir, f"売上集計結果_{timestamp}.csv")
    result.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n集計結果を保存しました: {output_file}")
    
    # 5. サマリー情報を表示
    print("\n" + "=" * 60)
    print("集計サマリー")
    print("=" * 60)
    print(f"商品数: {len(result)}商品")
    print(f"累計売上合計: ¥{result['累計売上'].sum():,.0f}")
    print("\nトップ10商品（累計売上順）:")
    print(result[['商品名', '商品カテゴリ①', '累計売上']].head(10).to_string(index=False))
    print("\n処理完了！")


if __name__ == "__main__":
    main()

