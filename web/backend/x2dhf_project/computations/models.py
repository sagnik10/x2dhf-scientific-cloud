from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator
class MolecularSystem(models.Model):
    SYMMETRY_CHOICES=[('C2v','C2v'),('Cs','Cs'),('C2','C2'),('Ci','Ci'),('D_inf_h','D_inf_h'),('C_inf_v','C_inf_v'),]
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    molecule_formula=models.CharField(max_length=255)
    geometry_type=models.CharField(max_length=50,choices=[('atom','Atom'),('diatomic','Diatomic'),('linear','Linear')])
    symmetry=models.CharField(max_length=50,choices=SYMMETRY_CHOICES,default='Cs')
    grid_spacing=models.FloatField(default=0.1,validators=[MinValueValidator(0.01),MaxValueValidator(1.0)])
    max_radius=models.FloatField(default=50.0,validators=[MinValueValidator(1),MaxValueValidator(500)])
    grid_size_x=models.IntegerField(default=200,validators=[MinValueValidator(50),MaxValueValidator(2000)])
    grid_size_y=models.IntegerField(default=200,validators=[MinValueValidator(50),MaxValueValidator(2000)])
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='molecular_systems')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        db_table='molecular_systems'
        indexes=[models.Index(fields=['user','-created_at']),]
class Computation(models.Model):
    STATUS_CHOICES=[('pending','Pending'),('running','Running'),('completed','Completed'),('failed','Failed'),('cancelled','Cancelled'),]
    THEORY_CHOICES=[('hf','Hartree-Fock'),('dft','Density Functional Theory'),('lda','Local Density Approximation'),('hfs','Hartree-Fock-Slater'),('oed','Optimized Effective Density'),('ted','Total Energy Density'),('scmc','SCMC'),('qe','Quantum Espresso'),]
    molecular_system=models.ForeignKey(MolecularSystem,on_delete=models.CASCADE,related_name='computations')
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='computations')
    title=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    theory=models.CharField(max_length=50,choices=THEORY_CHOICES,default='hf')
    functional=models.CharField(max_length=255,blank=True)
    engine=models.CharField(max_length=50,choices=[('x2dhf','X2DHF'),('quantum_espresso','Quantum Espresso')],default='x2dhf')
    spin_multiplicity=models.IntegerField(default=1,validators=[MinValueValidator(1),MaxValueValidator(10)])
    num_electrons=models.IntegerField(validators=[MinValueValidator(1)])
    basis_set=models.CharField(max_length=255,blank=True)
    scf_iterations=models.IntegerField(default=100,validators=[MinValueValidator(1),MaxValueValidator(5000000)])
    convergence_threshold=models.FloatField(default=1e-6,validators=[MinValueValidator(1e-10),MaxValueValidator(1e-3)])
    status=models.CharField(max_length=50,choices=STATUS_CHOICES,default='pending')
    task_id=models.CharField(max_length=255,blank=True)
    cpu_time_seconds=models.FloatField(null=True,blank=True)
    memory_usage_mb=models.FloatField(null=True,blank=True)
    error_message=models.TextField(blank=True)
    started_at=models.DateTimeField(null=True,blank=True)
    completed_at=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        db_table='computations'
        indexes=[models.Index(fields=['user','status']),models.Index(fields=['user','theory']),models.Index(fields=['-created_at']),]
class ComputationParameter(models.Model):
    computation=models.ForeignKey(Computation,on_delete=models.CASCADE,related_name='parameters')
    key=models.CharField(max_length=255)
    value=models.TextField()
    class Meta:
        db_table='computation_parameters'
        unique_together=['computation','key']
