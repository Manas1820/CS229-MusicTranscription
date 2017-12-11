# NOTE: **ALWAYS** add a trailing '/' at the end of a folder path

def config_1():
  # for outputing multiple notes
  return {
    'net': 'conv5',
    'annot_folder': '/root/new_data/mixed_context46/annot_melody3/',
    'image_folder': '/root/new_data/mixed_context46/image/',
    'sr_ratio': 6,
    'audio_type': 'MIX',
    'multiple': True,
    'save_dir': './output_model/multiple/',
    'save_prefix': 'model_conv5_multi_train',
    'use_pretrained': False, # whether or not to use a pretrained model
    'pretrained_path': './output_model/context46/model_conv5_train_epoch10.pt',
  }

def config_2():
  # for cqt images & single output
  return {
    'net': 'conv5',
    'annot_folder': '/root/new_data/context46/annot/',
    'image_folder': '/root/new_data/context46/cqt_image/',
    'sr_ratio': 6,
    'audio_type': 'RAW',
    'multiple': False,
    'save_dir': './output_model/context46/cqt/',
    'save_prefix': 'model_conv5_cqt_train',
    'use_pretrained': False, # whether or not to use a pretrained model
    'pretrained_path': './output_model/context46/model_conv5_train_epoch10.pt',
  }

def config_3():
  # for single output & smaller context
  return {
    'net': 'conv5',
    'annot_folder': '/root/new_data/context6/annot/',
    'image_folder': '/root/new_data/context6/image/',
    'sr_ratio': 1,
    'audio_type': 'RAW',
    'multiple': False,
    'save_dir': './output_model/context6/',
    'save_prefix': 'model_conv5_context6_train',
    'use_pretrained': False, # whether or not to use a pretrained model
    'pretrained_path': None,
  }
