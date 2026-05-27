from django.conf import settings
from django.db import models
from django.utils.text import slugify


class TheoryPost(models.Model):
    STATUS_CHOICES=[('draft','Draft'),('published','Published')]
    CATEGORY_CHOICES=[('hf','Hartree-Fock'),('dft','DFT'),('inputs','Input Cards'),('runtime','Runtime'),('physics','Physics')]
    title=models.CharField(max_length=180)
    slug=models.SlugField(max_length=220,unique=True,blank=True)
    category=models.CharField(max_length=30,choices=CATEGORY_CHOICES,default='physics')
    summary=models.CharField(max_length=280)
    body=models.TextField()
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='draft')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='theory_posts')
    seo_title=models.CharField(max_length=80,blank=True)
    seo_description=models.CharField(max_length=180,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    published_at=models.DateTimeField(null=True,blank=True)

    class Meta:
        ordering=['-updated_at']

    def save(self,*args,**kwargs):
        if not self.slug:
            base=slugify(self.title)[:190] or 'theory-post'
            slug=base
            index=2
            while TheoryPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug=f'{base}-{index}'
                index+=1
            self.slug=slug
        super().save(*args,**kwargs)

    def __str__(self):
        return self.title


class RuntimeControlPreset(models.Model):
    STATUS_CHOICES=[('draft','Draft'),('active','Active')]
    name=models.CharField(max_length=120)
    slug=models.SlugField(max_length=160,unique=True,blank=True)
    theory=models.CharField(max_length=30,default='hf')
    grid_spec=models.CharField(max_length=80,default='151 35.0')
    orbpot=models.CharField(max_length=80,default='hf')
    scf_iterations=models.PositiveIntegerField(default=1000)
    scf_orbital=models.FloatField(default=1e-6)
    scf_potential=models.FloatField(default=1e-6)
    advanced_cards=models.TextField(blank=True)
    explanation=models.TextField(blank=True)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='draft')
    created_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True,related_name='control_presets')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering=['theory','name']

    def save(self,*args,**kwargs):
        if not self.slug:
            base=slugify(self.name)[:135] or 'control-preset'
            slug=base
            index=2
            while RuntimeControlPreset.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug=f'{base}-{index}'
                index+=1
            self.slug=slug
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name
