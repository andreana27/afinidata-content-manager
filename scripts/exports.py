# Conversion a excel
import io
import xlsxwriter
from django.http import HttpResponse
from rest_framework.exceptions import ParseError


class ExcelExport():

    @staticmethod
    def excelResponse(querySet, columns_name=None, columns_field=None, filename='data'):

        try:
            offset = 0

            output = io.BytesIO()

            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()

            if columns_name is not None:
                offset = 1
                for col_num, value in enumerate(columns_name):
                    worksheet.write(0, col_num, value)

            for row_num, value in enumerate(querySet):
                col_num = 0
                for key in value.keys():
                    flag = True

                    if (columns_field is not None) and (key not in columns_field):
                        flag = False

                    if flag is True:
                        worksheet.write(row_num+offset, col_num, querySet[row_num][key])
                        col_num = col_num + 1

            workbook.close()

            output.seek(0)

            filename = '{}.xlsx'.format(filename)
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % filename

            return response
        except AttributeError:
            raise ParseError(detail="Error al parsear los datos")
