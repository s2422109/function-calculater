import requests
import flet as ft

# 地域情報のURL
AREA_URL = "http://www.jma.go.jp/bosai/forecast/data/forecast/012000.json"

# JSONデータを取得する関数
def fetch_weather_data():
    print(f"[INFO] 天気データを取得中: {AREA_URL}")
    try:
        response = requests.get(AREA_URL)
        if response.status_code == 200:
            print(f"[SUCCESS] 天気データ取得成功")
            return response.json()
        else:
            print(f"[ERROR] 天気データ取得失敗: ステータスコード {response.status_code}")
            return None
    except Exception as e:
        print(f"[EXCEPTION] 天気データ取得中にエラー発生: {e}")
        return None

# tempAverage と precipAverage の再帰的探索を行う関数
def extract_temp_precip(data):
    temp_average = None
    precip_average = None
    
    # リストの場合、各要素を再帰的に探索
    if isinstance(data, list):
        for item in data:
            temp_average, precip_average = extract_temp_precip(item)
            if temp_average and precip_average:  # 見つかったら戻る
                return temp_average, precip_average
    
    # 辞書の場合、tempAverage と precipAverage を取得
    if isinstance(data, dict):
        temp_average = data.get("tempAverage", None)
        precip_average = data.get("precipAverage", None)
    
    # tempAverage と precipAverage が存在すれば返す
    if temp_average is not None and precip_average is not None:
        temp_areas = temp_average.get("areas", [])
        precip_areas = precip_average.get("areas", [])
        
        # tempAverageのminとmaxを取得
        if temp_areas:
            temp_min = temp_areas[0].get("min", "情報なし")
            temp_max = temp_areas[0].get("max", "情報なし")
        else:
            temp_min = "情報なし"
            temp_max = "情報なし"

        # precipAverageのminとmaxを取得
        if precip_areas:
            precip_min = precip_areas[0].get("min", "情報なし")
            precip_max = precip_areas[0].get("max", "情報なし")
        else:
            precip_min = "情報なし"
            precip_max = "情報なし"

        return (temp_min, temp_max), (precip_min, precip_max)

    return None, None  # 見つからない場合は None を返す

# GUIアプリケーションを構築
def main(page: ft.Page):
    page.title = "地域タブの階層表示"
    page.scroll = ft.ScrollMode.AUTO

    # 天気データの取得
    weather_data = fetch_weather_data()

    if weather_data:
        # 'weather_data'がリストの場合、最初の要素を取得
        if isinstance(weather_data, list):
            print(f"[INFO] 'weather_data'はリスト型です。各要素を処理します。")

            # 各辞書に対して処理を行う
            time_info_controls = []
            for weather_entry in weather_data:
                publishing_office = weather_entry.get("publishingOffice", "不明")
                report_datetime = weather_entry.get("reportDatetime", "不明")
                time_series = weather_entry.get("timeSeries", [])

                print(f"[INFO] 発表局: {publishing_office}, 発表日時: {report_datetime}")
                
                if not time_series:
                    print("[ERROR] 'timeSeries'が見つかりませんでした")
                    continue

                # 各timeSeries内の情報を表示
                for series_index, series in enumerate(time_series):
                    print(f"[INFO] 処理中の timeSeries {series_index + 1}")

                    # timeDefinesとareasを取得
                    time_defines = series.get("timeDefines", [])
                    areas = series.get("areas", [])
                    print(f"[INFO] 'timeDefines'内のデータ数: {len(time_defines)}")
                    print(f"[INFO] 'areas'内のエリア数: {len(areas)}")

                    # 各areaについて処理
                    for area in areas:
                        area_name = area.get("area", {}).get("name", "不明")
                        area_code = area.get("area", {}).get("code", "不明")

                        # 各種データを取得
                        weather_codes = area.get("weatherCodes", [])
                        weathers = area.get("weathers", [])
                        winds = area.get("winds", [])
                        waves = area.get("waves", [])
                        pops = area.get("pops", [])  # 降水確率
                        reliabilities = area.get("reliabilities", [])  # 信頼度
                        temps = area.get("temps", [])  # 温度 (必要に応じて)

                        # 各timeDefineに対応する情報を表示
                        for idx, time_define in enumerate(time_defines):
                            # 日時情報を表示
                            time_label = f"日時: {time_define}"

                            # 各日の天気情報を取得
                            weather_code = weather_codes[idx] if idx < len(weather_codes) else "情報なし"
                            weather = weathers[idx] if idx < len(weathers) else "情報なし"
                            wind = winds[idx] if idx < len(winds) else "情報なし"
                            wave = waves[idx] if idx < len(waves) else "情報なし"
                            pop = pops[idx] if idx < len(pops) else "情報なし"
                            reliability = reliabilities[idx] if idx < len(reliabilities) else "情報なし"
                            temp = temps[idx] if idx < len(temps) else "情報なし"

                            # tempAverage と precipAverage を抽出
                            temp_average, precip_average = extract_temp_precip(weather_entry)
                            temp_min, temp_max = temp_average if temp_average else ("情報なし", "情報なし")
                            precip_min, precip_max = precip_average if precip_average else ("情報なし", "情報なし")

                            # 各日の情報をまとめて表示
                            day_info = f"発表局: {publishing_office}\n発表日時: {report_datetime}\nエリア: {area_name}\n日時: {time_label}\n天気コード: {weather_code}\n天気: {weather}\n風: {wind}\n波: {wave}\n降水確率: {pop}\n信頼度: {reliability}\n温度: {temp}\n温度Min: {temp_min}\n温度Max: {temp_max}\n降水確率Min: {precip_min}\n降水確率Max: {precip_max}"
                            time_info_controls.append(ft.Text(value=day_info))

            # ボタンで結果を表示
            content_text = ft.Text(value="天気データを確認するにはボタンを押してください。")

            def on_check_weather(e, text=content_text):
                text.value = "天気データが表示されています。"
                text.update()

            # ページに結果を表示
            page.add(
                ft.Column(
                    controls=[
                        content_text,
                        *time_info_controls,  # 各日の天気データを追加
                        ft.ElevatedButton(
                            text="確認",
                            on_click=on_check_weather
                        ),
                    ]
                )
            )

    else:
        page.add(ft.Text("天気データの取得に失敗しました。"))

# Fletアプリを開始
ft.app(target=main)
