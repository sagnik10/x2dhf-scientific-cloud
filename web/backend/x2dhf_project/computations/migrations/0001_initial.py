from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Computation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('theory', models.CharField(choices=[('hf', 'Hartree-Fock'), ('dft', 'Density Functional Theory'), ('lda', 'Local Density Approximation'), ('qe', 'Quantum Espresso')], default='hf', max_length=50)),
                ('functional', models.CharField(blank=True, max_length=255)),
                ('engine', models.CharField(choices=[('x2dhf', 'X2DHF'), ('quantum_espresso', 'Quantum Espresso')], default='x2dhf', max_length=50)),
                ('spin_multiplicity', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)])),
                ('num_electrons', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('basis_set', models.CharField(blank=True, max_length=255)),
                ('scf_iterations', models.IntegerField(default=100, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10000)])),
                ('convergence_threshold', models.FloatField(default=1e-06, validators=[django.core.validators.MinValueValidator(1e-10), django.core.validators.MaxValueValidator(0.001)])),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'), ('cancelled', 'Cancelled')], default='pending', max_length=50)),
                ('task_id', models.CharField(blank=True, max_length=255)),
                ('cpu_time_seconds', models.FloatField(blank=True, null=True)),
                ('memory_usage_mb', models.FloatField(blank=True, null=True)),
                ('error_message', models.TextField(blank=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'computations',
            },
        ),
        migrations.CreateModel(
            name='MolecularSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('molecule_formula', models.CharField(max_length=255)),
                ('geometry_type', models.CharField(choices=[('atom', 'Atom'), ('diatomic', 'Diatomic'), ('linear', 'Linear')], max_length=50)),
                ('symmetry', models.CharField(choices=[('C2v', 'C2v'), ('Cs', 'Cs'), ('C2', 'C2'), ('Ci', 'Ci'), ('D_inf_h', 'D_inf_h'), ('C_inf_v', 'C_inf_v')], default='Cs', max_length=50)),
                ('grid_spacing', models.FloatField(default=0.1, validators=[django.core.validators.MinValueValidator(0.01), django.core.validators.MaxValueValidator(1.0)])),
                ('max_radius', models.FloatField(default=50.0, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(500)])),
                ('grid_size_x', models.IntegerField(default=200, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(2000)])),
                ('grid_size_y', models.IntegerField(default=200, validators=[django.core.validators.MinValueValidator(50), django.core.validators.MaxValueValidator(2000)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='molecular_systems', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'molecular_systems',
            },
        ),
        migrations.CreateModel(
            name='ComputationParameter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('value', models.TextField()),
                ('computation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parameters', to='computations.computation')),
            ],
            options={
                'db_table': 'computation_parameters',
            },
        ),
        migrations.AddField(
            model_name='computation',
            name='molecular_system',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='computations', to='computations.molecularsystem'),
        ),
        migrations.AddField(
            model_name='computation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='computations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='molecularsystem',
            index=models.Index(fields=['user', '-created_at'], name='molecular_s_user_id_0092ee_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='computationparameter',
            unique_together={('computation', 'key')},
        ),
        migrations.AddIndex(
            model_name='computation',
            index=models.Index(fields=['user', 'status'], name='computation_user_id_8a017c_idx'),
        ),
        migrations.AddIndex(
            model_name='computation',
            index=models.Index(fields=['user', 'theory'], name='computation_user_id_78311d_idx'),
        ),
        migrations.AddIndex(
            model_name='computation',
            index=models.Index(fields=['-created_at'], name='computation_created_5429e2_idx'),
        ),
    ]
