from django.core.management.base import BaseCommand
from surveys.models import Survey, AnswerSheet, Grade
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "survey_pk",
            help="Survey primary key or id to generate the report.",
        )

    def handle(self, *args, **options):
        survey = Survey.objects.get(pk=options["survey_pk"])
        answer_sheets = AnswerSheet.objects.filter(survey=survey)
        completed_surveys = 0

        def get_initial_grades():
            return {
                "Nulo": 0,
                "Bajo": 0,
                "Medio": 0,
                "Alto": 0,
                "Muy alto": 0,
            }

        report = {
            "categoria": {
                "Ambiente de trabajo": get_initial_grades(),
                "Factores propios de la actividad": get_initial_grades(),
                "Organización del tiempo de trabajo": get_initial_grades(),
                "Liderazgo y relaciones en el trabajo": get_initial_grades(),
                "Entorno organizacional": get_initial_grades(),
            },
            "domino": {
                "Condiciones en el ambiente de trabajo": get_initial_grades(),
                "Carga de trabajo": get_initial_grades(),
                "Falta de control sobre el trabajo": get_initial_grades(),
                "Jornada de trabajo": get_initial_grades(),
                "Interferencia en la relación trabajo-familia": get_initial_grades(),
                "Liderazgo": get_initial_grades(),
                "Relaciones en el trabajo": get_initial_grades(),
                "Violencia": get_initial_grades(),
                "Reconocimiento del desempeño": get_initial_grades(),
                "Insuficiente sentido de pertenencia e inestabilidad": get_initial_grades(),
            },
        }
        for answer_sheet in answer_sheets:
            grades = Grade.objects.filter(answer_sheet=answer_sheet.pk)
            for grade in grades:
                if grade:
                    completed_surveys += 1
                    report["categoria"]["Ambiente de trabajo"][
                        grade.work_environment
                    ] += 1
                    report["categoria"]["Factores propios de la actividad"][
                        grade.working_load
                    ] += 1
                    report["categoria"]["Organización del tiempo de trabajo"][
                        grade.work_lack_control
                    ] += 1
                    report["categoria"]["Liderazgo y relaciones en el trabajo"][
                        grade.leadership_relationship
                    ] += 1

                    report["domino"]["Condiciones en el ambiente de trabajo"][
                        grade.work_environment_conditions
                    ] += 1
                    report["domino"]["Carga de trabajo"][grade.working_load] += 1
                    report["domino"]["Falta de control sobre el trabajo"][
                        grade.work_lack_control
                    ] += 1
                    report["domino"]["Jornada de trabajo"][grade.working_day] += 1
                    report["domino"]["Interferencia en la relación trabajo-familia"][
                        grade.family_work_relationship
                    ] += 1
                    report["domino"]["Liderazgo"][grade.leadership] += 1
                    report["domino"]["Relaciones en el trabajo"][
                        grade.work_relationship
                    ] += 1
                    report["domino"]["Violencia"][grade.violence] += 1

                    if survey.guide_number == 3:
                        report["categoria"]["Entorno organizacional"][
                            grade.organizational_environment
                        ] += 1
                        report["domino"]["Reconocimiento del desempeño"][
                            grade.performance_recognition
                        ] += 1
                        report["domino"][
                            "Insuficiente sentido de pertenencia e inestabilidad"
                        ][grade.sense_belonging_instability] += 1
        for k, v in report.items():
            for k1, v1 in v.items():
                for k2, v2 in v1.items():
                    report[k][k1][k2] = round((v2 / completed_surveys) * 100, 2)

        print(report)
        with open(f"/tmp/report_{survey.guide_number}.json", "w") as file:
            json.dump(report, file)
