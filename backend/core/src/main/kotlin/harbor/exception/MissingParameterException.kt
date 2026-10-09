package harbor.exception

import harbor.enums.ProductGroup

/** A required `parameter_set` value is not configured for the requested scope (configuration error) -> HTTP 500. */
class MissingParameterException(key: String, productGroup: ProductGroup?, country: String?, scopeValue: String?) :
    IllegalStateException("Parameter '$key' not configured for scope [$productGroup, $country, $scopeValue]")
