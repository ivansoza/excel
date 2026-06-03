from django.shortcuts import render
from django import forms
import pandas as pd
from django.http import HttpResponse


class UploadFileForm(forms.Form):
    file = forms.FileField()



def home(request):
    return render(request, 'home.html')


def upload_excel2(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if str(file).endswith('.xlsx'):
                df = pd.read_excel(file)
            elif str(file).endswith('.csv'):
                df = pd.read_csv(file)
            else:
                return HttpResponse("Por favor, sube un archivo .xlsx o .csv válido.")

            # Creación de 'nombre del dentista'
            df['nombre del dentista'] = df['nombreprestador'] + " " + df['primerapellidoprestador'] + " " + df['segundoapellidoprestador']

            age_ranges = {
                '< 1 año': (0, 0),
                '1 año': (1, 1),
                '2-4 años': (2, 4),
                '5-9 años': (5, 9),
                '10-14 años': (10, 14),
                '15-19 años': (15, 19),
                '20-29 años': (20, 29),
                '30-49 años': (30, 49),
                '50-59 años': (50, 59),
                '60 y más años': (60, 200)
            }
            index_labels = ['Total de Consultas por curpprestador'] + [f'{age} mujer primer año' for age in age_ranges.keys()] + \
                           [f'{age} hombre primer año' for age in age_ranges.keys()] + \
                           ['Total por sexo (Hombre)', 'Total por sexo (Mujer)']

            display_df = pd.DataFrame(index=index_labels)

            # Agregamos los nombres del dentista como fila adicional
            nombres_df = pd.DataFrame()

            # Total de consultas por curpprestador y nombres
            df_filtered = df[df['primeravezanio'] == 1]
            total_counts = df_filtered.groupby('curpprestador').agg({'curpprestador': 'count', 'nombre del dentista': 'first'}).rename(columns={'curpprestador': 'Total de Consultas'})
            for curp, data in total_counts.iterrows():
                display_df[curp] = [data['Total de Consultas']] + [0] * (len(age_ranges) * 2 + 2)
                nombres_df[curp] = [data['nombre del dentista']]

            # Concatenar los nombres al principio de display_df
            display_df = pd.concat([nombres_df, display_df])

            # Aplicación de filtros
            for label, (low, high) in age_ranges.items():
                for sexo in [1, 2]:
                    df_range = df_filtered[(df_filtered['sexo'] == sexo) & (df_filtered['edad'] >= low) & (df_filtered['edad'] <= high)]
                    range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} {("mujer" if sexo == 2 else "hombre")} primer año')
                    for _, r in range_counts.iterrows():
                        display_df.at[f'{label} {("mujer" if sexo == 2 else "hombre")} primer año', r['curpprestador']] = r[f'{label} {("mujer" if sexo == 2 else "hombre")} primer año']

            total_by_sex = df_filtered.groupby(['curpprestador', 'sexo'])['curpprestador'].count().reset_index(name='Total por Sexo')
            for _, row in total_by_sex.iterrows():
                sex_label = 'Total por sexo (Hombre)' if row['sexo'] == 1 else 'Total por sexo (Mujer)'
                curp_details = f"{row['curpprestador']}"
                display_df.at[sex_label, curp_details] = row['Total por Sexo']

            display_df_html = display_df.to_html()

            return render(request, 'procesador_excel/display.html', {'dataframe': display_df_html})
    else:
        form = UploadFileForm()
    return render(request, 'procesador_excel/upload.html', {'form': form})

def upload_excel(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if str(file).endswith('.xlsx'):
                df = pd.read_excel(file)
            elif str(file).endswith('.csv'):
                df = pd.read_csv(file)
            else:
                return HttpResponse("Por favor, sube un archivo .xlsx o .csv válido.")

            # Creación de 'nombre del dentista'
            df['nombre del dentista'] = df['nombreprestador'] + " " + df['primerapellidoprestador'] + " " + df['segundoapellidoprestador']

            age_ranges = {
                '< 1 año': (0, 0),
                '1 año': (1, 1),
                '2-4 años': (2, 4),
                '5-9 años': (5, 9),
                '10-14 años': (10, 14),
                '15-19 años': (15, 19),
                '20-29 años': (20, 29),
                '30-49 años': (30, 49),
                '50-59 años': (50, 59),
                '60 y más años': (60, 200)
            }
            index_labels = ['Total de Consultas por curpprestador'] + [f'{age} mujer primera vez' for age in age_ranges.keys()] + \
                           [f'{age} mujer segunda vez' for age in age_ranges.keys()] + \
                           [f'{age} hombre primera vez' for age in age_ranges.keys()] + \
                           [f'{age} hombre segunda vez' for age in age_ranges.keys()] + \
                           ['Total por sexo (Hombre)', 'Total por sexo (Mujer)']

            display_df = pd.DataFrame(index=index_labels)

            # Agregamos los nombres del dentista como fila adicional
            nombres_df = pd.DataFrame()

            # Total de consultas por curpprestador y nombres
            total_counts = df.groupby('curpprestador').agg({'curpprestador': 'count', 'nombre del dentista': 'first'}).rename(columns={'curpprestador': 'Total de Consultas'})
            for curp, data in total_counts.iterrows():
                display_df[curp] = [data['Total de Consultas']] + [0] * (len(age_ranges) * 4 + 2)
                nombres_df[curp] = [data['nombre del dentista']]

            # Concatenar los nombres al principio de display_df
            display_df = pd.concat([nombres_df, display_df])

            # Aplicación de filtros
            for label, (low, high) in age_ranges.items():
                for sexo in [1, 2]:
                    for relaciontemporal, suffix in zip([0, 1], ['primera vez', 'segunda vez']):
                        df_range = df[(df['sexo'] == sexo) & (df['edad'] >= low) & (df['edad'] <= high) & (df['relaciontemporal'] == relaciontemporal)]
                        range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} {("mujer" if sexo == 2 else "hombre")} {suffix}')
                        for _, r in range_counts.iterrows():
                            display_df.at[f'{label} {("mujer" if sexo == 2 else "hombre")} {suffix}', r['curpprestador']] = r[f'{label} {("mujer" if sexo == 2 else "hombre")} {suffix}']


            total_by_sex = df.groupby(['curpprestador', 'sexo'])['curpprestador'].count().reset_index(name='Total por Sexo')
            for _, row in total_by_sex.iterrows():
                sex_label = 'Total por sexo (Hombre)' if row['sexo'] == 1 else 'Total por sexo (Mujer)'
                curp_details = f"{row['curpprestador']}"
                display_df.at[sex_label, curp_details] = row['Total por Sexo']

            display_df_html = display_df.to_html()

            return render(request, 'procesador_excel/display.html', {'dataframe': display_df_html})
    else:
        form = UploadFileForm()
    return render(request, 'procesador_excel/upload.html', {'form': form})



import re
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render

def upload_excel3(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            # --- 1) Leer archivo ---
            if str(file).endswith('.xlsx'):
                df = pd.read_excel(file)
            elif str(file).endswith('.csv'):
                df = pd.read_csv(file)
            else:
                return HttpResponse("Por favor, sube un archivo .xlsx o .csv válido.")

            # --- 2) Normalizar nombres de columnas + mapear sinónimos ---
            def norm_col(s: str) -> str:
                s = str(s).strip().lower()
                s = re.sub(r"\s+", "", s)         # quita espacios internos: "pieza temp" -> "piezatemp"
                s = re.sub(r"[^a-z0-9_]", "", s)  # quita caracteres raros
                return s

            df.columns = [norm_col(c) for c in df.columns]

            alias_to_canonical = {
                # Diente temporal / pieza temporal (variantes)
                "piezatemp": "piezatemp",
                "piezatemporal": "piezatemp",
                "dientetemp": "piezatemp",
                "dientetemporal": "piezatemp",

                # Diente permanente / pieza permanente (variantes)
                "piezaperm": "piezaperm",
                "piezapermanente": "piezaperm",
                "dienteperm": "piezaperm",
                "dientepermanente": "piezaperm",
            }

            rename_map = {c: alias_to_canonical[c] for c in df.columns if c in alias_to_canonical}
            df = df.rename(columns=rename_map)

            # --- 3) Validar columnas obligatorias (para no tener KeyError en otras partes) ---
            required_cols = [
                "nombreprestador", "primerapellidoprestador", "segundoapellidoprestador",
                "curpprestador", "edad"
            ]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                return HttpResponse(
                    f"Faltan columnas obligatorias: {missing}. "
                    f"Columnas detectadas: {list(df.columns)}"
                )

            # Si NO vienen estas columnas opcionales, créalas en 0 para que no truene el filtro
            optional_numeric_cols = [
                "piezatemp", "piezaperm", "pulpar", "fosetasfisuras", "amalgamas", "resinas",
                "ionomerovidrio", "materialtemp", "otrasatenciones", "radiografias"
            ]
            for c in optional_numeric_cols:
                if c not in df.columns:
                    df[c] = 0

            # Asegurar numéricos en las columnas tipo "cantidad"
            for c in optional_numeric_cols:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

            # --- 4) Creación de 'nombre del dentista' ---
            df['nombre del dentista'] = (
                df['nombreprestador'].astype(str) + " " +
                df['primerapellidoprestador'].astype(str) + " " +
                df['segundoapellidoprestador'].astype(str)
            )

            # Rangos de edad actuales
            age_ranges = {
                '< de 10 años': (0, 9),
                '10 a 19 años': (10, 19),
                '20-59 años': (20, 59),
                '60 y más años': (60, 200)
            }

            # Nuevos rangos de edad para barnizfluor
            age_ranges_barnizfluor = {
                '1 a 5 años de edad': (1, 5),
                '6 a 19 años de edad': (6, 19),
                '20 y más años de edad': (20, 200)
            }

            # Actualización de index_labels
            index_labels = ['Total de Consultas por curpprestador'] + \
                        [f'{age} con placa bacteriana' for age in age_ranges.keys()] + \
                        ['Total con placa bacteriana'] + \
                        [f'{age} con cepillado' for age in age_ranges.keys()] + \
                        ['Total con cepillado'] + \
                        [f'{age} con hilodental' for age in age_ranges.keys()] + \
                        ['Total con hilodental'] + \
                        ['Total con fluor'] + \
                        [f'{age} con barnizfluor' for age in age_ranges_barnizfluor.keys()] + \
                        ['Total con barnizfluor'] + \
                        [f'{age} con pulido' for age in age_ranges.keys()] + \
                        ['Total con pulido'] + \
                        ['Total con raspado'] + \
                        ['Total con protesis'] + \
                        ['Total con tejidos bucales'] + \
                        ['Total con autoexamen'] + \
                        ['Total con fosetas y fisuras'] + \
                        ['Total con amalgamas'] + \
                        ['Total con resinas'] + \
                        ['Total con ionomerovidrio'] + \
                        ['Total con material temporal'] + \
                        ['Total con Diente temporal'] + \
                        ['Total con Diente permanente'] + \
                        ['Total con pulpar'] + \
                        ['Total con cirugia bucal'] + \
                        ['Total con farmacoterapia'] + \
                        ['Total con otras atenciones'] + \
                        ['Total con radiografias'] + \
                        ['Total con tratamiento integral']

            display_df = pd.DataFrame(index=index_labels)

            # Agregamos los nombres del dentista como fila adicional
            nombres_df = pd.DataFrame()

            total_counts = (
                df.groupby('curpprestador')
                  .agg({'curpprestador': 'count', 'nombre del dentista': 'first'})
                  .rename(columns={'curpprestador': 'Total de Consultas'})
            )

            for curp, data in total_counts.iterrows():
                display_df[curp] = [data['Total de Consultas']] + [0] * (len(index_labels) - 1)
                nombres_df[curp] = [data['nombre del dentista']]

            # Concatenar los nombres al principio de display_df
            display_df = pd.concat([nombres_df, display_df])

            # ======= TU CÓDIGO ORIGINAL (sin cambios relevantes) =======
            df_filtered_placa = df[df['placabacteriana'] == 1]
            for label, (low, high) in age_ranges.items():
                df_range = df_filtered_placa[(df_filtered_placa['edad'] >= low) & (df_filtered_placa['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con placa bacteriana')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con placa bacteriana', r['curpprestador']] = r[f'{label} con placa bacteriana']

            total_placa = df_filtered_placa.groupby('curpprestador').size().reset_index(name='Total con placa bacteriana')
            for _, row in total_placa.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con placa bacteriana', curp_details] = row['Total con placa bacteriana']

            df_filtered_cepillado = df[df['cepillado'] == 1]
            for label, (low, high) in age_ranges.items():
                df_range = df_filtered_cepillado[(df_filtered_cepillado['edad'] >= low) & (df_filtered_cepillado['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con cepillado')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con cepillado', r['curpprestador']] = r[f'{label} con cepillado']

            total_cepillado = df_filtered_cepillado.groupby('curpprestador').size().reset_index(name='Total con cepillado')
            for _, row in total_cepillado.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con cepillado', curp_details] = row['Total con cepillado']

            df_filtered_hilodental = df[df['hilodental'] == 1]
            for label, (low, high) in age_ranges.items():
                df_range = df_filtered_hilodental[(df_filtered_hilodental['edad'] >= low) & (df_filtered_hilodental['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con hilodental')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con hilodental', r['curpprestador']] = r[f'{label} con hilodental']

            total_hilodental = df_filtered_hilodental.groupby('curpprestador').size().reset_index(name='Total con hilodental')
            for _, row in total_hilodental.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con hilodental', curp_details] = row['Total con hilodental']

            df_filtered_fluor = df[df['fluor'] == 1]
            total_fluor = df_filtered_fluor.groupby('curpprestador').size().reset_index(name='Total con fluor')
            for _, row in total_fluor.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con fluor', curp_details] = row['Total con fluor']

            df_filtered_barnizfluor = df[df['barnizfluor'] == 1]
            for label, (low, high) in age_ranges_barnizfluor.items():
                df_range = df_filtered_barnizfluor[(df_filtered_barnizfluor['edad'] >= low) & (df_filtered_barnizfluor['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con barnizfluor')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con barnizfluor', r['curpprestador']] = r[f'{label} con barnizfluor']

            total_barnizfluor = df_filtered_barnizfluor.groupby('curpprestador').size().reset_index(name='Total con barnizfluor')
            for _, row in total_barnizfluor.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con barnizfluor', curp_details] = row['Total con barnizfluor']

            df_filtered_profilaxis = df[df['profilaxis'] == 1]
            for label, (low, high) in age_ranges.items():
                df_range = df_filtered_profilaxis[(df_filtered_profilaxis['edad'] >= low) & (df_filtered_profilaxis['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con pulido')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con pulido', r['curpprestador']] = r[f'{label} con pulido']

            total_pulido = df_filtered_profilaxis.groupby('curpprestador').size().reset_index(name='Total con pulido')
            for _, row in total_pulido.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con pulido', curp_details] = row['Total con pulido']

            df_filtered_odontoxesis = df[df['odontoxesis'] == 1]
            total_raspado = df_filtered_odontoxesis.groupby('curpprestador').size().reset_index(name='Total con raspado')
            for _, row in total_raspado.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con raspado', curp_details] = row['Total con raspado']

            df_filtered_protesis = df[df['protesis'] == 1]
            total_protesis = df_filtered_protesis.groupby('curpprestador').size().reset_index(name='Total con protesis')
            for _, row in total_protesis.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con protesis', curp_details] = row['Total con protesis']

            df_filtered_tejidosbucales = df[df['tejidosbucales'] == 1]
            total_tejidos_bucales = df_filtered_tejidosbucales.groupby('curpprestador').size().reset_index(name='Total con tejidos bucales')
            for _, row in total_tejidos_bucales.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con tejidos bucales', curp_details] = row['Total con tejidos bucales']

            df_filtered_autoexamen = df[df['autoexamen'] == 1]
            total_autoexamen = df_filtered_autoexamen.groupby('curpprestador').size().reset_index(name='Total con autoexamen')
            for _, row in total_autoexamen.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con autoexamen', curp_details] = row['Total con autoexamen']

            df_filtered_fosetasfisuras = df[df['fosetasfisuras'] > 0]
            total_fosetasfisuras = df_filtered_fosetasfisuras.groupby('curpprestador')['fosetasfisuras'].sum().reset_index(name='Total con fosetas y fisuras')
            for _, row in total_fosetasfisuras.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con fosetas y fisuras', curp_details] = row['Total con fosetas y fisuras']

            df_filtered_amalgamas = df[df['amalgamas'] > 0]
            total_amalgamas = df_filtered_amalgamas.groupby('curpprestador')['amalgamas'].sum().reset_index(name='Total con amalgamas')
            for _, row in total_amalgamas.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con amalgamas', curp_details] = row['Total con amalgamas']

            df_filtered_resinas = df[df['resinas'] > 0]
            total_resinas = df_filtered_resinas.groupby('curpprestador')['resinas'].sum().reset_index(name='Total con resinas')
            for _, row in total_resinas.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con resinas', curp_details] = row['Total con resinas']

            df_filtered_ionomerovidrio = df[df['ionomerovidrio'] > 0]
            total_ionomerovidrio = df_filtered_ionomerovidrio.groupby('curpprestador')['ionomerovidrio'].sum().reset_index(name='Total con ionomerovidrio')
            for _, row in total_ionomerovidrio.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con ionomerovidrio', curp_details] = row['Total con ionomerovidrio']

            df_filtered_materialtemp = df[df['materialtemp'] > 0]
            total_materialtemp = df_filtered_materialtemp.groupby('curpprestador')['materialtemp'].sum().reset_index(name='Total con material temporal')
            for _, row in total_materialtemp.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con material temporal', curp_details] = row['Total con material temporal']

            # ✅ YA NO TRUENA aunque venga como "pieza temp" o "diente temp"
            df_filtered_piezatemp = df[df['piezatemp'] > 0]
            total_piezatemp = df_filtered_piezatemp.groupby('curpprestador')['piezatemp'].sum().reset_index(name='Total con Diente temporal')
            for _, row in total_piezatemp.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con Diente temporal', curp_details] = row['Total con Diente temporal']

            df_filtered_piezaperm = df[df['piezaperm'] > 0]
            total_piezaperm = df_filtered_piezaperm.groupby('curpprestador')['piezaperm'].sum().reset_index(name='Total con Diente permanente')
            for _, row in total_piezaperm.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con Diente permanente', curp_details] = row['Total con Diente permanente']

            df_filtered_pulpar = df[df['pulpar'] > 0]
            total_pulpar = df_filtered_pulpar.groupby('curpprestador')['pulpar'].sum().reset_index(name='Total con pulpar')
            for _, row in total_pulpar.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con pulpar', curp_details] = row['Total con pulpar']

            df_filtered_cirugiabucal = df[df['cirugiabucal'] == 1]
            total_cirugiabucal = df_filtered_cirugiabucal.groupby('curpprestador').size().reset_index(name='Total con cirugia bucal')
            for _, row in total_cirugiabucal.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con cirugia bucal', curp_details] = row['Total con cirugia bucal']

            df_filtered_farmacoterapia = df[df['farmacoterapia'] == 1]
            total_farmacoterapia = df_filtered_farmacoterapia.groupby('curpprestador').size().reset_index(name='Total con farmacoterapia')
            for _, row in total_farmacoterapia.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con farmacoterapia', curp_details] = row['Total con farmacoterapia']

            df_filtered_otrasatenciones = df[df['otrasatenciones'] > 0]
            total_otrasatenciones = df_filtered_otrasatenciones.groupby('curpprestador')['otrasatenciones'].sum().reset_index(name='Total con otras atenciones')
            for _, row in total_otrasatenciones.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con otras atenciones', curp_details] = row['Total con otras atenciones']

            df_filtered_radiografias = df[df['radiografias'] > 0]
            total_radiografias = df_filtered_radiografias.groupby('curpprestador')['radiografias'].sum().reset_index(name='Total con radiografias')
            for _, row in total_radiografias.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con radiografias', curp_details] = row['Total con radiografias']

            df_filtered_tratamientointegral = df[df['tratamientointegral'] == 1]
            total_tratamientointegral = df_filtered_tratamientointegral.groupby('curpprestador').size().reset_index(name='Total con tratamiento integral')
            for _, row in total_tratamientointegral.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con tratamiento integral', curp_details] = row['Total con tratamiento integral']
            # ======= FIN TU CÓDIGO ORIGINAL =======

            display_df_html = display_df.to_html()
            return render(request, 'procesador_excel/display.html', {'dataframe': display_df_html})

    else:
        form = UploadFileForm()

    return render(request, 'procesador_excel/upload.html', {'form': form})
