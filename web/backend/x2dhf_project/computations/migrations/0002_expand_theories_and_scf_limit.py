from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("computations", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="computation",
            name="theory",
            field=models.CharField(
                choices=[
                    ("hf", "Hartree-Fock"),
                    ("dft", "Density Functional Theory"),
                    ("lda", "Local Density Approximation"),
                    ("hfs", "Hartree-Fock-Slater"),
                    ("oed", "Optimized Effective Density"),
                    ("ted", "Total Energy Density"),
                    ("scmc", "SCMC"),
                    ("qe", "Quantum Espresso"),
                ],
                default="hf",
                max_length=50,
            ),
        ),
        migrations.AlterField(
            model_name="computation",
            name="scf_iterations",
            field=models.IntegerField(
                default=100,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5000000),
                ],
            ),
        ),
    ]
