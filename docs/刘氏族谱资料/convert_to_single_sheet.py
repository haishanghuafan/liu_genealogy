#!/usr/bin/env python3
"""
将 genealogy_data.xlsx（多表结构）转换为 liu_genealog.xlsx（单表结构）
"""

import pandas as pd
import os

def convert_to_single_sheet():
    input_path = "genealogy_data.xlsx"
    output_path = "liu_genealog.xlsx"

    # 读取四个工作表
    df_persons = pd.read_excel(input_path, sheet_name="人物")
    df_generations = pd.read_excel(input_path, sheet_name="世代")
    df_branches = pd.read_excel(input_path, sheet_name="支系")
    df_spouses = pd.read_excel(input_path, sheet_name="配偶关系")

    print(f"读取数据：{len(df_persons)} 人物, {len(df_generations)} 世代, {len(df_branches)} 支系, {len(df_spouses)} 配偶关系")

    # 创建世代映射：世代名称 -> 世代数
    gen_number_map = {}
    for _, row in df_generations.iterrows():
        if pd.notna(row.get("世代名称")):
            gen_name = str(row["世代名称"]).strip()
            gen_num = int(row["世代数"]) if pd.notna(row.get("世代数")) else None
            gen_number_map[gen_name] = gen_num

    # 创建支系映射：支系名称 -> 描述
    branch_desc_map = {}
    for _, row in df_branches.iterrows():
        if pd.notna(row.get("支系名称")):
            branch_name = str(row["支系名称"]).strip()
            branch_desc = str(row["描述"]) if pd.notna(row.get("描述")) else ""
            branch_desc_map[branch_name] = branch_desc

    # 创建配偶映射：姓名 -> 配偶姓名
    spouse_map = {}
    for _, row in df_spouses.iterrows():
        husband = str(row["丈夫姓名"]).strip() if pd.notna(row.get("丈夫姓名")) else None
        wife = str(row["妻子姓名"]).strip() if pd.notna(row.get("妻子姓名")) else None
        if husband and wife:
            spouse_map[husband] = wife
            spouse_map[wife] = husband

    # 构建单表数据
    single_sheet_data = []

    for _, row in df_persons.iterrows():
        name = str(row["姓名"]).strip() if pd.notna(row.get("姓名")) else ""
        if not name:
            continue

        # 基本信息
        gender = str(row.get("性别", "男")).strip()
        is_spouse = str(row.get("是否为外族配偶", "否")).strip()

        # 世代信息
        gen_name = str(row["世代名称"]).strip() if pd.notna(row.get("世代名称")) else ""
        gen_number = gen_number_map.get(gen_name, "")

        # 支系信息
        branch_name = str(row["所属支系"]).strip() if pd.notna(row.get("所属支系")) else ""
        branch_desc = branch_desc_map.get(branch_name, "")

        # 家庭关系
        father_name = str(row["父亲姓名"]).strip() if pd.notna(row.get("父亲姓名")) else ""
        mother_name = str(row["母亲姓名"]).strip() if pd.notna(row.get("母亲姓名")) else ""
        spouse_name = spouse_map.get(name, "")

        # 称谓信息
        courtesy_name = str(row["字"]).strip() if pd.notna(row.get("字")) else ""
        art_name = str(row["号"]).strip() if pd.notna(row.get("号")) else ""
        alias = str(row["别名"]).strip() if pd.notna(row.get("别名")) else ""
        generation_char = str(row["辈份字"]).strip() if pd.notna(row.get("辈份字")) else ""

        # 生卒信息
        birth_year = int(row["出生年份"]) if pd.notna(row.get("出生年份")) else ""
        death_year = int(row["逝世年份"]) if pd.notna(row.get("逝世年份")) else ""
        birth_place = str(row["出生地"]).strip() if pd.notna(row.get("出生地")) else ""

        # 墓葬信息
        burial_place = str(row["葬地"]).strip() if pd.notna(row.get("葬地")) else ""
        burial_fengshui = str(row["墓形/风水"]).strip() if pd.notna(row.get("墓形/风水")) else ""
        burial_direction = str(row["坐向"]).strip() if pd.notna(row.get("坐向")) else ""

        # 文字描述
        biography = str(row["生平简介"]).strip() if pd.notna(row.get("生平简介")) else ""
        achievements = str(row["主要事迹"]).strip() if pd.notna(row.get("主要事迹")) else ""
        descendants_location = str(row["后裔分布"]).strip() if pd.notna(row.get("后裔分布")) else ""

        # 其他
        notes = str(row["备注"]).strip() if pd.notna(row.get("备注")) else ""
        sort_order = int(row["排序"]) if pd.notna(row.get("排序")) else ""

        single_sheet_data.append({
            "姓名": name,
            "性别": gender,
            "是否为外族配偶": is_spouse,
            "世代数": gen_number,
            "世代名称": gen_name,
            "支系名称": branch_name,
            "支系描述": branch_desc,
            "父亲姓名": father_name,
            "母亲姓名": mother_name,
            "配偶姓名": spouse_name,
            "字": courtesy_name,
            "号": art_name,
            "别名": alias,
            "辈份字": generation_char,
            "出生年份": birth_year,
            "逝世年份": death_year,
            "出生地": birth_place,
            "葬地": burial_place,
            "墓形/风水": burial_fengshui,
            "坐向": burial_direction,
            "生平简介": biography,
            "主要事迹": achievements,
            "后裔分布": descendants_location,
            "备注": notes,
            "排序": sort_order,
        })

    # 创建 DataFrame
    df_single = pd.DataFrame(single_sheet_data)

    # 按世代数和排序排序
    df_single['世代数_num'] = pd.to_numeric(df_single['世代数'], errors='coerce').fillna(999)
    df_single['排序_num'] = pd.to_numeric(df_single['排序'], errors='coerce').fillna(999)
    df_single = df_single.sort_values(['世代数_num', '排序_num'])
    df_single = df_single.drop(columns=['世代数_num', '排序_num'])

    # 保存为 Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_single.to_excel(writer, sheet_name='族谱人物数据', index=False)

        # 添加字段说明工作表
        help_data = [
            ["字段名", "说明", "示例值"],
            ["姓名", "人物姓名", "刘邦"],
            ["性别", "男/女", "男"],
            ["是否为外族配偶", "是/否，标记嫁入/入赘人员", "否"],
            ["世代数", "数字，如1,2,3", "1"],
            ["世代名称", "如'第1世'", "第1世"],
            ["支系名称", "所属支系名称", "沛县支系"],
            ["支系描述", "支系说明", "始祖刘邦所在支系"],
            ["父亲姓名", "父亲姓名，用于建立父子关系", "刘邦"],
            ["母亲姓名", "母亲姓名，用于建立母子关系", "吕雉"],
            ["配偶姓名", "主要配偶姓名，用于建立配偶关系", "吕雉"],
            ["字", "表字", "季"],
            ["号", "别号", ""],
            ["别名", "其他名称", ""],
            ["辈份字", "辈分字", ""],
            ["出生年份", "出生年份，公元前用负数", "-256"],
            ["逝世年份", "逝世年份，公元前用负数", "-195"],
            ["出生地", "出生地点", "江苏徐州"],
            ["葬地", "安葬地点", ""],
            ["墓形/风水", "墓葬形制", ""],
            ["坐向", "墓葬坐向", ""],
            ["生平简介", "人物简介", "汉高祖，汉朝开国皇帝"],
            ["主要事迹", "重要事迹", "建立汉朝，统一中国"],
            ["后裔分布", "后代分布情况", ""],
            ["备注", "其他备注", ""],
            ["排序", "同世代内排序，数字越小越靠前", "1"],
        ]
        df_help = pd.DataFrame(help_data[1:], columns=help_data[0])
        df_help.to_excel(writer, sheet_name='字段说明', index=False)

    print(f"成功创建 {output_path}")
    print(f"共 {len(df_single)} 条人物记录")
    print(f"世代范围: {df_single['世代数'].min()} - {df_single['世代数'].max()}")

if __name__ == "__main__":
    convert_to_single_sheet()
