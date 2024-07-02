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



def upload_excel3(request):
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
                        ['Total con tejidos bucales']+\
                        ['Total con autoexamen']+\
                        ['Total con fosetas y fisuras']+\
                        ['Total con amalgamas']+\
                        ['Total con resinas']+\
                        ['Total con ionomerovidrio'] + \
                        ['Total con material temporal'] + \
                        ['Total con Diente temporal'] + \
                        ['Total con Diente permanente']+ \
                        ['Total con pulpar'] + \
                        ['Total con cirugia bucal'] + \
                        ['Total con farmacoterapia'] + \
                        ['Total con otras atenciones'] + \
                        ['Total con radiografias'] + \
                        ['Total con tratamiento integral']

        

            display_df = pd.DataFrame(index=index_labels)

            # Agregamos los nombres del dentista como fila adicional
            nombres_df = pd.DataFrame()

            total_counts = df.groupby('curpprestador').agg({'curpprestador': 'count', 'nombre del dentista': 'first'}).rename(columns={'curpprestador': 'Total de Consultas'})
            for curp, data in total_counts.iterrows():
                display_df[curp] = [data['Total de Consultas']] + [0] * (len(index_labels) - 1)  # Ajusta la longitud aquí
                nombres_df[curp] = [data['nombre del dentista']]




            # Concatenar los nombres al principio de display_df
            display_df = pd.concat([nombres_df, display_df])

            # Filtrar por placabacteriana igual a 1
            df_filtered_placa = df[df['placabacteriana'] == 1]

            # Aplicación de filtros por rangos de edad para placa bacteriana
            for label, (low, high) in age_ranges.items():
                df_range = df_filtered_placa[(df_filtered_placa['edad'] >= low) & (df_filtered_placa['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con placa bacteriana')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con placa bacteriana', r['curpprestador']] = r[f'{label} con placa bacteriana']

            # Total con placa bacteriana por curpprestador
            total_placa = df_filtered_placa.groupby('curpprestador').size().reset_index(name='Total con placa bacteriana')
            for _, row in total_placa.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con placa bacteriana', curp_details] = row['Total con placa bacteriana']

            # Filtrar por cepillado igual a 1
            df_filtered_cepillado = df[df['cepillado'] == 1]

            # Aplicación de filtros por rangos de edad para cepillado
            for label, (low, high) in age_ranges.items():
                df_range = df_filtered_cepillado[(df_filtered_cepillado['edad'] >= low) & (df_filtered_cepillado['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con cepillado')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con cepillado', r['curpprestador']] = r[f'{label} con cepillado']

            # Total con cepillado por curpprestador
            total_cepillado = df_filtered_cepillado.groupby('curpprestador').size().reset_index(name='Total con cepillado')
            for _, row in total_cepillado.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con cepillado', curp_details] = row['Total con cepillado']

            # Filtrar por hilodental igual a 1
            df_filtered_hilodental = df[df['hilodental'] == 1]

            # Aplicación de filtros por rangos de edad para hilodental
            for label, (low, high) in age_ranges.items():
                df_range = df_filtered_hilodental[(df_filtered_hilodental['edad'] >= low) & (df_filtered_hilodental['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con hilodental')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con hilodental', r['curpprestador']] = r[f'{label} con hilodental']

            # Total con hilodental por curpprestador
            total_hilodental = df_filtered_hilodental.groupby('curpprestador').size().reset_index(name='Total con hilodental')
            for _, row in total_hilodental.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con hilodental', curp_details] = row['Total con hilodental']

            # Filtrar por fluor igual a 1
            df_filtered_fluor = df[df['fluor'] == 1]

            # Total con fluor por curpprestador
            total_fluor = df_filtered_fluor.groupby('curpprestador').size().reset_index(name='Total con fluor')
            for _, row in total_fluor.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con fluor', curp_details] = row['Total con fluor']

            # Filtrar por barnizfluor igual a 1
            df_filtered_barnizfluor = df[df['barnizfluor'] == 1]

            # Aplicación de filtros por rangos de edad para barnizfluor
            for label, (low, high) in age_ranges_barnizfluor.items():
                df_range = df_filtered_barnizfluor[(df_filtered_barnizfluor['edad'] >= low) & (df_filtered_barnizfluor['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con barnizfluor')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con barnizfluor', r['curpprestador']] = r[f'{label} con barnizfluor']

            # Total con barnizfluor por curpprestador
            total_barnizfluor = df_filtered_barnizfluor.groupby('curpprestador').size().reset_index(name='Total con barnizfluor')
            for _, row in total_barnizfluor.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con barnizfluor', curp_details] = row['Total con barnizfluor']


            # Filtrar por profilaxis igual a 1
            df_filtered_profilaxis = df[df['profilaxis'] == 1]

            # Aplicación de filtros por rangos de edad para pulido
            for label, (low, high) in age_ranges.items():
                df_range = df_filtered_profilaxis[(df_filtered_profilaxis['edad'] >= low) & (df_filtered_profilaxis['edad'] <= high)]
                range_counts = df_range.groupby('curpprestador').size().reset_index(name=f'{label} con pulido')
                for _, r in range_counts.iterrows():
                    display_df.at[f'{label} con pulido', r['curpprestador']] = r[f'{label} con pulido']

            # Total con pulido por curpprestador
            total_pulido = df_filtered_profilaxis.groupby('curpprestador').size().reset_index(name='Total con pulido')
            for _, row in total_pulido.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con pulido', curp_details] = row['Total con pulido']

            # Filtrar por odontoxesis igual a 1
            df_filtered_odontoxesis = df[df['odontoxesis'] == 1]

            # Total con raspado por curpprestador
            total_raspado = df_filtered_odontoxesis.groupby('curpprestador').size().reset_index(name='Total con raspado')
            for _, row in total_raspado.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con raspado', curp_details] = row['Total con raspado']

            # Filtrar por protesis igual a 1
            df_filtered_protesis = df[df['protesis'] == 1]

            # Total con protesis por curpprestador
            total_protesis = df_filtered_protesis.groupby('curpprestador').size().reset_index(name='Total con protesis')
            for _, row in total_protesis.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con protesis', curp_details] = row['Total con protesis']

            # Filtrar por tejidosbucales igual a 1
            df_filtered_tejidosbucales = df[df['tejidosbucales'] == 1]

            # Total con tejidos bucales por curpprestador
            total_tejidos_bucales = df_filtered_tejidosbucales.groupby('curpprestador').size().reset_index(name='Total con tejidos bucales')
            for _, row in total_tejidos_bucales.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con tejidos bucales', curp_details] = row['Total con tejidos bucales']

            df_filtered_autoexamen = df[df['autoexamen'] == 1]

            # Total con tejidos bucales por curpprestador
            total_autoexamen = df_filtered_autoexamen.groupby('curpprestador').size().reset_index(name='Total con autoexamen')
            for _, row in total_autoexamen.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con autoexamen', curp_details] = row['Total con autoexamen']


            df_filtered_fosetasfisuras = df[df['fosetasfisuras'] == 1]

            # Total con tejidos bucales por curpprestador
            total_fosetasfisuras= df_filtered_fosetasfisuras.groupby('curpprestador').size().reset_index(name='Total con fosetas y fisuras')
            for _, row in total_fosetasfisuras.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con fosetas y fisuras', curp_details] = row['Total con fosetas y fisuras']

            df_filtered_amalgamas = df[df['amalgamas'] == 1]

            # Total con tejidos bucales por curpprestador
            total_amalgamas= df_filtered_amalgamas.groupby('curpprestador').size().reset_index(name='Total con amalgamas')
            for _, row in total_amalgamas.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con amalgamas', curp_details] = row['Total con amalgamas']

            df_filtered_resinas = df[df['resinas'] == 1]

            # Total con tejidos bucales por curpprestador
            total_resinas= df_filtered_resinas.groupby('curpprestador').size().reset_index(name='Total con resinas')
            for _, row in total_resinas.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con resinas', curp_details] = row['Total con resinas']

            # Filtrar por ionomerovidrio igual a 1
            df_filtered_ionomerovidrio = df[df['ionomerovidrio'] == 1]

            # Total con ionomerovidrio por curpprestador
            total_ionomerovidrio = df_filtered_ionomerovidrio.groupby('curpprestador').size().reset_index(name='Total con ionomerovidrio')
            for _, row in total_ionomerovidrio.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con ionomerovidrio', curp_details] = row['Total con ionomerovidrio']

            # Filtrar por material temporal igual a 1
            df_filtered_materialtemp = df[df['materialtemp'] == 1]

            # Total con material temporal por curpprestador
            total_materialtemp = df_filtered_materialtemp.groupby('curpprestador').size().reset_index(name='Total con material temporal')
            for _, row in total_materialtemp.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con material temporal', curp_details] = row['Total con material temporal']

            # Filtrar por Diente temporal igual a 1
            df_filtered_piezatemp = df[df['piezatemp'] == 1]

            # Total con Diente temporal por curpprestador
            total_piezatemp = df_filtered_piezatemp.groupby('curpprestador').size().reset_index(name='Total con Diente temporal')
            for _, row in total_piezatemp.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con Diente temporal', curp_details] = row['Total con Diente temporal']

            # Filtrar por Diente permanente igual a 1
            df_filtered_piezaperm = df[df['piezaperm'] == 1]

            # Total con Diente permanente por curpprestador
            total_piezaperm = df_filtered_piezaperm.groupby('curpprestador').size().reset_index(name='Total con Diente permanente')
            for _, row in total_piezaperm.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con Diente permanente', curp_details] = row['Total con Diente permanente']


            # Filtrar por pulpar igual a 1
            df_filtered_pulpar = df[df['pulpar'] == 1]

            # Total con pulpar por curpprestador
            total_pulpar = df_filtered_pulpar.groupby('curpprestador').size().reset_index(name='Total con pulpar')
            for _, row in total_pulpar.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con pulpar', curp_details] = row['Total con pulpar']

            # Filtrar por cirugiabucal igual a 1
            df_filtered_cirugiabucal = df[df['cirugiabucal'] == 1]

            # Total con cirugia bucal por curpprestador
            total_cirugiabucal = df_filtered_cirugiabucal.groupby('curpprestador').size().reset_index(name='Total con cirugia bucal')
            for _, row in total_cirugiabucal.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con cirugia bucal', curp_details] = row['Total con cirugia bucal']

            # Filtrar por farmacoterapia igual a 1
            df_filtered_farmacoterapia = df[df['farmacoterapia'] == 1]

            # Total con farmacoterapia por curpprestador
            total_farmacoterapia = df_filtered_farmacoterapia.groupby('curpprestador').size().reset_index(name='Total con farmacoterapia')
            for _, row in total_farmacoterapia.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con farmacoterapia', curp_details] = row['Total con farmacoterapia']

            # Filtrar por otrasatenciones igual a 1
            df_filtered_otrasatenciones = df[df['otrasatenciones'] == 1]

            # Total con otras atenciones por curpprestador
            total_otrasatenciones = df_filtered_otrasatenciones.groupby('curpprestador').size().reset_index(name='Total con otras atenciones')
            for _, row in total_otrasatenciones.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con otras atenciones', curp_details] = row['Total con otras atenciones']

            # Filtrar por radiografias igual a 1
            df_filtered_radiografias = df[df['radiografias'] == 1]

            # Total con radiografias por curpprestador
            total_radiografias = df_filtered_radiografias.groupby('curpprestador').size().reset_index(name='Total con radiografias')
            for _, row in total_radiografias.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con radiografias', curp_details] = row['Total con radiografias']

            # Filtrar por tratamientointegral igual a 1
            df_filtered_tratamientointegral = df[df['tratamientointegral'] == 1]

            # Total con tratamiento integral por curpprestador
            total_tratamientointegral = df_filtered_tratamientointegral.groupby('curpprestador').size().reset_index(name='Total con tratamiento integral')
            for _, row in total_tratamientointegral.iterrows():
                curp_details = f"{row['curpprestador']}"
                display_df.at['Total con tratamiento integral', curp_details] = row['Total con tratamiento integral']


            display_df_html = display_df.to_html()

            return render(request, 'procesador_excel/display.html', {'dataframe': display_df_html})
    else:
        form = UploadFileForm()
    return render(request, 'procesador_excel/upload.html', {'form': form})
